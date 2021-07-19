from labelbox.data.serialization.ndjson.converter import NDJsonConverter

payload = [{
    'answer': {
        'schemaId': 'ckrb1sfl8099g0y91cxbd5ftb'
    },
    'schemaId': 'ckrb1sfkn099c0y910wbo0p1a',
    'dataRow': {
        'id': 'ckrb1sf1i1g7i0ybcdc6oc8ct'
    },
    'schemaId': 'ckrb1sfjx099a0y914hl319ie',
    'uuid': 'f6879f59-d2b5-49c2-aceb-d9e8dc478673'
}, {
    'answer': [{
        'schemaId': 'ckrb1sfl8099e0y919v260awv'
    }],
    'schemaId': 'ckrb1sfkn099c0y910wbo0p1a',
    'dataRow': {
        'id': 'ckrb1sf1i1g7i0ybcdc6oc8ct'
    },
    'uuid': 'd009925d-91a3-4f67-abd9-753453f5a584'
}, {
    'answer': "a value",
    'schemaId': 'ckrb1sfkn099c0y910wbo0p1a',
    'dataRow': {
        'id': 'ckrb1sf1i1g7i0ybcdc6oc8ct'
    },
    'uuid': 'd009925d-91a3-4f67-abd9-753453f5a584'
}]


def test_classification():
    res = NDJsonConverter.deserialize(payload)
    res.data = list(res.data)
    res = list(NDJsonConverter.serialize(res))
    assert res == payload
