import re


def add_page_to_annotation(annotation):
    if 'neonion' in annotation \
            and 'context' in annotation['neonion'] \
            and 'oa' in annotation \
            and 'hasTarget' in annotation['oa'] \
            and 'hasSource' in annotation['oa']['hasTarget'] \
            and '@id' in annotation['oa']['hasTarget']['hasSource']:
        url = annotation['oa']['hasTarget']['hasSource']['@id']

        match = re.search('\?pn=(.+)', url)
        if match:
            # extract page number parameter from url
            annotation['neonion']['context']['pageNum'] = int(match.group(0))
        else:
            annotation['neonion']['context']['pageNum'] = annotation['neonion']['context']['pageIdx'] + 1

    return annotation
