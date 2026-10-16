"""Read-only live smoke replay of the separately frozen conversation cases."""
import json
from pathlib import Path
from time import perf_counter
from app.ai.api.rag_v2_endpoint import RAGV2ChatAdapter
from app.ai.schemas.chat import ChatRequest


def main():
    directory = Path(__file__).resolve().parents[2] / 'docs' / 'ai'
    frozen = json.loads((directory / 'rag_v2_conversation_fresh_cases.json').read_text(encoding='utf-8'))
    adapter = RAGV2ChatAdapter()
    results = []
    for case in frozen['cases']:
        started = perf_counter()
        try:
            response = adapter.run(ChatRequest(question=case['question'], conversation_id=case['conversation_id']), history=case['history'])
            audit = response._rag_v2_provenance
            result = dict(id=case['id'], expected=case['expected'], answer=response.answer, sources=response.sources,
                          status=audit['status'], conversation_reason=audit.get('conversation_reason'),
                          conversation_product_ids=audit.get('conversation_product_ids'),
                          abstention_reason=audit.get('abstention_reason'), accepted_claims=len(audit['citations']))
        except Exception as error:
            result = dict(id=case['id'], technical_failure=type(error).__name__, message=str(error))
        result['seconds'] = round(perf_counter() - started, 3)
        results.append(result)
        print(json.dumps(result, ensure_ascii=True), flush=True)
    output = directory / 'rag_v2_conversation_fresh_results.json'
    if output.exists():
        raise RuntimeError('Refusing to overwrite an existing evaluation artifact')
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
