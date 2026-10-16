"""Explicit local catalog cleanup. Keeps named accounts and their chat history.

Default is a read-only preview. --apply requires a verified PostgreSQL backup.
No Qdrant, embedding, indexing, extraction or checkpoint operations are used.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
import app.models
from app.database import Base, SessionLocal, engine
from app.config import settings
from app.models.user import UserRole
from app.models.product import Product, ProductStatus
from app.models.course import Course, CourseCategory, CourseLevel, CourseStatus
from app.models.course_instructor import CourseInstructor
from app.models.product_instructor import ProductInstructor
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.resource import Resource
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from sqlalchemy import delete, func, inspect, select, text

KEEP_EMAILS = ('admin@buildlearn.local', 'mo@gmail.com', 'akrout@gmail.com')
MANIFEST = Path(__file__).parent / 'data/buildlearn_catalog.json'


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding='utf-8'))


def keep_users(db):
    users = {u.email: u for u in db.query(User).filter(User.email.in_(KEEP_EMAILS))}
    if set(users) != set(KEEP_EMAILS):
        raise ValueError('All three requested accounts must exist before cleanup')
    roles = (UserRole.ADMIN, UserRole.INSTRUCTOR, UserRole.STUDENT)
    if any(users[email].role != role for email, role in zip(KEEP_EMAILS, roles)):
        raise ValueError('Expected admin, instructor and student roles; cleanup stopped')
    return users


def counts(db):
    return {t.name: db.execute(select(func.count()).select_from(t)).scalar_one()
            for t in Base.metadata.sorted_tables}


def source_documents(manifest):
    catalog = json.loads((BACKEND / 'ai_data/identity/product_identity_catalog.json').read_text(encoding='utf-8'))
    result = []
    for spec in manifest['products']:
        product = next(p for p in catalog['products'] if p['canonical_name'] == spec['canonical_name'])
        if spec['document_id'] not in product['document_ids']:
            raise ValueError('Manifest/source identity mismatch: ' + spec['name'])
        source = next(s for s in product['source_files'] if s['document_id'] == spec['document_id'])
        path = (BACKEND / source['source_path'].replace('\\', '/')).resolve()
        if not path.is_relative_to((BACKEND / 'ai_data/raw').resolve()) or not path.is_file():
            raise ValueError('Missing or unsafe source document')
        result.append((path, source['file_name']))
    return result


def reset_and_seed(db, manifest, resource_urls):
    """Caller owns the transaction; failure must roll back the entire reset."""
    users = keep_users(db)
    keep_ids = [u.id for u in users.values()]
    removed_conversations = select(Conversation.id).where(Conversation.user_id.not_in(keep_ids))
    db.execute(delete(Message).where(Message.conversation_id.in_(removed_conversations)))
    db.execute(delete(Conversation).where(Conversation.user_id.not_in(keep_ids)))
    # Reset learning activities and demo notifications, preserving retained chats.
    for table in reversed(Base.metadata.sorted_tables):
        if table.name not in ('users', 'conversations', 'messages'):
            db.execute(delete(table))
    db.execute(delete(User).where(User.id.not_in(keep_ids)))
    instructor = users['mo@gmail.com']
    for spec, resource_url in zip(manifest['products'], resource_urls, strict=True):
        category = CourseCategory.ETANCHEITE if spec['category'] == 'ETANCHEITE' else CourseCategory(spec['category'])
        product = Product(name=spec['name'], category=category.value,
                          description=spec['description'], status=ProductStatus.PUBLISHED)
        db.add(product); db.flush()
        db.add(ProductInstructor(product_id=product.id, instructor_id=instructor.id))
        duration = sum(l['minutes'] for m in spec['modules'] for l in m['lessons'])
        course = Course(instructor_id=instructor.id, product_id=product.id, title=spec['title'],
                        description=spec['description'], objectives=spec['objectives'],
                        category=category, level=CourseLevel.BEGINNER, language='French',
                        duration=duration, status=CourseStatus.PUBLISHED)
        db.add(course); db.flush()
        db.add(CourseInstructor(course_id=course.id, instructor_id=instructor.id))
        for index, module_spec in enumerate(spec['modules']):
            module = Module(course_id=course.id, title=module_spec['title'], order_index=index)
            db.add(module); db.flush()
            for lesson_index, lesson_spec in enumerate(module_spec['lessons']):
                lesson = Lesson(module_id=module.id, title=lesson_spec['title'],
                                content=lesson_spec['content'], duration_minutes=lesson_spec['minutes'],
                                order_index=lesson_index, is_published=True)
                db.add(lesson); db.flush()
                if index == 0 and lesson_index == 0:
                    db.add(Resource(lesson_id=lesson.id, title='Fiche technique : ' + spec['name'],
                                    url=resource_url, resource_type='application/pdf',
                                    description='Document fabricant déjà acquis ; vérifier sa version et ses limites avant application.'))
        quiz = Quiz(course_id=course.id, title='Évaluation : ' + spec['name'],
                    description='Deux questions automatiques et une réponse écrite corrigée par le formateur.')
        db.add(quiz); db.flush()
        for index, question_spec in enumerate(spec['questions']):
            question = Question(quiz_id=quiz.id, text=question_spec['text'],
                                question_type=question_spec['type'], points=question_spec['points'], order_index=index)
            if question.question_type == 'yes_no':
                question.answers = [Answer(text='Yes', is_correct=question_spec['correct_yes']),
                                    Answer(text='No', is_correct=not question_spec['correct_yes'])]
            db.add(question)
    db.flush()
    if db.query(User).count() != 3 or db.query(Course).count() != len(manifest['products']):
        raise ValueError('Post-reset integrity check failed')


def database_backup(destination):
    pg_dump = shutil.which('pg_dump') or r'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe'
    if not Path(pg_dump).is_file():
        raise RuntimeError('pg_dump is required before any destructive cleanup')
    url = engine.url
    env = dict(os.environ)
    env['PGPASSWORD'] = url.password or ''
    args = [pg_dump, '--format=custom', '--file', str(destination), '--host', url.host,
            '--port', str(url.port or 5432), '--username', url.username, url.database]
    completed = subprocess.run(args, env=env, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError('Database backup failed; cleanup stopped')
    verify = subprocess.run([str(Path(pg_dump).with_name('pg_restore.exe')), '--list', str(destination)], capture_output=True)
    if verify.returncode != 0 or destination.stat().st_size == 0:
        raise RuntimeError('Backup verification failed; cleanup stopped')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Back up, then replace the local learning catalog')
    args = parser.parse_args()
    manifest = load_manifest()
    sources = source_documents(manifest)
    with SessionLocal() as db:
        keep_users(db)
        before = counts(db)
    preview = dict(keep=list(KEEP_EMAILS), before=before, products=[p['name'] for p in manifest['products']],
                   courses=[p['title'] for p in manifest['products']],
                   preserved='Retained account IDs/passwords/roles and chat histories; Qdrant/indexing unchanged',
                   reset='Other users; all old courses/products and associated learning activity; old notifications')
    if not args.apply:
        print(json.dumps(preview, ensure_ascii=True, indent=2)); return
    if engine.dialect.name != 'postgresql':
        raise RuntimeError('Live cleanup is restricted to the configured PostgreSQL database')
    expected = set(Base.metadata.tables) | {'alembic_version'}
    if set(inspect(engine).get_table_names()) != expected:
        raise RuntimeError('Unexpected database tables; cleanup stopped')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
    backup_dir = BACKEND / '.local_backups' / ('catalog-reset-' + stamp)
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup_file = backup_dir / 'database.dump'
    database_backup(backup_file)
    upload_root = settings.upload_path
    destination = upload_root / 'academy' / stamp
    destination.mkdir(parents=True, exist_ok=False)
    urls = []; copied = []; committed = False
    try:
        for index, (path, filename) in enumerate(sources):
            target = destination / f'source-{index+1}.pdf'
            shutil.copy2(path, target)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != hashlib.sha256(target.read_bytes()).hexdigest():
                raise RuntimeError('Document copy integrity failed')
            urls.append('/uploads/' + target.relative_to(upload_root).as_posix())
            copied.append(dict(file_name=filename, sha256=digest))
        with SessionLocal() as db, db.begin():
            db.execute(text("SET LOCAL lock_timeout = '5s'"))
            tables = ', '.join('"' + t.name + '"' for t in Base.metadata.sorted_tables)
            db.execute(text('LOCK TABLE ' + tables + ' IN EXCLUSIVE MODE'))
            reset_and_seed(db, manifest, urls)
            after = counts(db)
        committed = True
        summary = dict(**preview, after=after, backup=str(backup_file), source_copies=copied)
        (backup_dir / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    except Exception:
        # Only the newly created files are cleaned up; original uploads are retained.
        if not committed:
            for path in destination.glob('*.pdf'): path.unlink()
            destination.rmdir()
        raise


if __name__ == '__main__':
    main()
