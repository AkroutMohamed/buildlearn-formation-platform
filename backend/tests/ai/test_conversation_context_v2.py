"""Fresh bounded conversation scenarios; no previous quality labels are reused."""
from app.ai.rag.product_identity import ProductIdentityResolver
from app.ai.rag.conversation_context_v2 import resolve_followup
import pytest


@pytest.fixture(scope='module')
def resolver():
    return ProductIdentityResolver.load()


def user(content):
    return dict(role='user', content=content)


@pytest.mark.parametrize('question', ['Et sa consommation ?', 'What is its weight?', 'Quelle est son épaisseur ?', 'dimensions ?'])
def test_single_product_followup(resolver, question):
    result = resolve_followup(question, [user('Parlons du produit LIKA PAP2.'), user(question)], resolver, 'saved-conversation')
    assert result.reason is None
    assert result.product_ids == resolver.resolve('LIKA PAP2').resolved_product_ids
    assert result.question.lower().endswith('(lika pap2)')


def test_new_chat_does_not_inherit_history(resolver):
    result = resolve_followup('Et sa consommation ?', [user('LIKA PAP2')], resolver, None)
    assert result.reason == 'missing_conversation_product'


def test_comparison_requires_clarification(resolver):
    result = resolve_followup('Et son poids ?', [user('Comparer LIKA PAP2 avec LIKA FINA')], resolver, 'saved')
    assert result.reason == 'ambiguous_conversation_product'


def test_switch_product(resolver):
    result = resolve_followup('Et sa consommation ?', [user('LIKA PAP2'), user('LIKA FINA')], resolver, 'saved')
    assert result.product_ids == resolver.resolve('LIKA FINA').resolved_product_ids


def test_unknown_variant_cannot_restore_previous_product(resolver):
    result = resolve_followup('Et sa consommation ?', [user('LIKA PAP2'), user('LIKA PAP2 EXTRAUNKNOWN')], resolver, 'saved')
    assert result.reason == 'ambiguous_conversation_product'


def test_assistant_output_cannot_switch_product(resolver):
    result = resolve_followup('Et sa consommation ?', [user('LIKA PAP2'), dict(role='assistant', content='LIKA FINA')], resolver, 'saved')
    assert result.product_ids == resolver.resolve('LIKA PAP2').resolved_product_ids


def test_explicit_question_is_never_rewritten(resolver):
    question = 'Consommation pour LIKA FINA ?'
    assert resolve_followup(question, [user('LIKA PAP2')], resolver, 'saved').question == question


def test_missing_product_clarifies(resolver):
    assert resolve_followup('Et sa consommation ?', [user('Bonjour')], resolver, 'saved').reason == 'missing_conversation_product'


def test_non_followup_does_not_receive_product(resolver):
    question = 'Expliquez les règles de sécurité générales.'
    assert resolve_followup(question, [user('LIKA PAP2')], resolver, 'saved').question == question


def test_adapter_clarification_skips_retrieval_and_generation(resolver):
    from unittest.mock import Mock
    from app.ai.api.rag_v2_endpoint import RAGV2ChatAdapter
    from app.ai.rag.hierarchical_rag_v2 import HierarchicalRAGV2, RAGV2Config
    from app.ai.schemas.chat import ChatRequest
    retriever, llm = Mock(), Mock()
    service = HierarchicalRAGV2(retriever=retriever, llm=llm, identity_resolver=resolver, config=RAGV2Config(model='qwen2.5-coder:7b'))
    response = RAGV2ChatAdapter(lambda: service).run(ChatRequest(question='Et sa consommation ?'))
    assert response.sources == []
    assert response._rag_v2_provenance['conversation_reason'] == 'missing_conversation_product'
    retriever.retrieve.assert_not_called()
    llm.generate_grounded.assert_not_called()


def test_adapter_passes_only_resolved_question_to_pipeline(resolver, monkeypatch):
    from unittest.mock import Mock
    from app.ai.api.rag_v2_endpoint import RAGV2ChatAdapter
    from app.ai.rag.hierarchical_rag_v2 import HierarchicalRAGV2, RAGV2Config, RAGV2Response
    from app.ai.schemas.chat import ChatRequest
    questions = []
    def run(self, question):
        questions.append(question)
        return RAGV2Response('insufficient', False, question, [], [], self.config.model, {})
    monkeypatch.setattr(HierarchicalRAGV2, 'run', run)
    service = HierarchicalRAGV2(retriever=Mock(), llm=Mock(), identity_resolver=resolver, config=RAGV2Config(model='qwen2.5-coder:7b'))
    response = RAGV2ChatAdapter(lambda: service).run(ChatRequest(question='Et sa consommation ?', conversation_id='saved'), history=[user('LIKA PAP2')])
    assert questions == ['Et sa consommation ? (lika pap2)']
    assert response._rag_v2_provenance['conversation_product_ids'] == list(resolver.resolve('LIKA PAP2').resolved_product_ids)
