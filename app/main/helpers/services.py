import functools
import operator
import re
from datetime import datetime
from flask import abort, current_app
from flask_login import current_user

from dmutils.apiclient import APIError
from dmutils.formats import format_field_based_price
from dmutils.service_attribute import Attribute

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def get_drafts(apiclient, supplier_id, framework_slug):
    try:
        drafts = apiclient.find_draft_services(
            current_user.supplier_id,
            framework=framework_slug
        )['services']

    except APIError as e:
        abort(e.status_code)

    complete_drafts = [draft for draft in drafts if draft['status'] == 'submitted']
    drafts = [draft for draft in drafts if draft['status'] == 'not-submitted']

    return drafts, complete_drafts


def get_lot_drafts(apiclient, supplier_id, framework_slug, lot_slug):
    drafts, complete_drafts = get_drafts(apiclient, supplier_id, framework_slug)
    return (
        [draft for draft in drafts if draft['lot'] == lot_slug],
        [draft for draft in complete_drafts if draft['lot'] == lot_slug]
    )


def count_unanswered_questions(service_attributes):
    unanswered_required, unanswered_optional = (0, 0)
    for section in service_attributes:
        for question in section['rows']:
            if question.answer_required:
                unanswered_required += 1
            elif question.value in ['', [], None]:
                unanswered_optional += 1

    return unanswered_required, unanswered_optional


def reformat_pricing_data(service_data, service_questions):
    nest_questions = [x.questions for x in service_questions.sections]
    questions = functools.reduce(operator.add, nest_questions, [])
    pricing_questions = [x for x in questions if x['type'] == "pricing" and "fields" in x]
    for question in pricing_questions:
        name = question['id']
        service_data[name] = format_field_based_price(service_data, question)
    return service_data


def get_service_attributes(service_data, service_questions):
    return list(map(
        lambda section: {
            'name': section['name'],
            'rows': _get_rows(section, service_data),
            'editable': section['editable'],
            'id': section['id']
        },
        service_questions
    ))


def _get_rows(section, service_data):
    return list(
        map(
            lambda question: Attribute(
                value=service_data.get(question['id'], None),
                question_type=question['type'],
                label=question['question'],
                optional=question.get('optional', False)
            ),
            section['questions']
        )
    )


def is_service_associated_with_supplier(service):
    return service.get('supplierId') == current_user.supplier_id


def is_service_modifiable(service):
    return service.get('status') != 'disabled'


def get_draft_document_url(uploader, document_path):
    url = uploader.get_signed_url(document_path)
    if url is not None:
        url = urlparse.urlparse(url)
        base_url = urlparse.urlparse(current_app.config['DM_G7_DRAFT_DOCUMENTS_URL'])
        return url._replace(netloc=base_url.netloc, scheme=base_url.scheme).geturl()


def parse_document_upload_time(data):
    match = re.search("(\d{4}-\d{2}-\d{2}-\d{2}\d{2})\..{2,3}$", data)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d-%H%M")


def get_next_section_name(content, current_section_id):
    if content.get_next_editable_section_id(current_section_id):
        return content.get_section(
            content.get_next_editable_section_id(current_section_id)
        ).name
