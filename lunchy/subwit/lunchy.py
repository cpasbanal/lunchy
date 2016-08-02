# import models
from lunchy.models import Person, Availability

# import wit specific module
from lunchy.subwit.common import first_entity_value
# import lunchy specific submodule
from lunchy.sublunchy.lunch import handle_lunch

import dateutil.parser

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger("lunchy")


def set_availability(request):
    logger.debug("** Start setting availaibility... **")
    # get the info from the bot
    context = request['context']
    entities = request['entities']
    logger.debug("Got entities: " + str(entities))
    # clean up previous requests by removing these keys from the context dict
    context.pop("lunchCreated", None)
    context.pop("missingEmail", None)
    context.pop("notEnoughGuests", None)

    # store all the context information in a specific namespace to avoid conflict
    if not "lunchy" in context:
        context["lunchy"] = {}

    # check if nickname is given, else use user_name
    nickname = first_entity_value(entities, 'contact') if entities else None
    if nickname:
        context["lunchy"]["nickname"] = nickname
    else: #no contact found, check if not already in namespace lunchy and not None
        if "nickname" in context["lunchy"] and not context["lunchy"]["nickname"]:
            # then, use user_name
            context["lunchy"]["nickname"] = context['user_name']
    logger.debug("Availability nickname is: " + str(context["lunchy"]["nickname"]) + ". The one given in argument was: " + str(nickname))

    # get user date given by user or given in a previous context
    user_date = first_entity_value(entities, 'datetime') if entities else None
    if user_date:
        context["lunchy"]["datetime"] = user_date
        # remove previous error from context
        context.pop("missingDatetime", None)

    # if no date is given, raise an error
    if not "datetime" in context.get("lunchy", None): # no date given
        logger.debug("No date given and context: " + str(context))
        context['missingDatetime'] = True
    else: # try create the availability
        # query the database to see if user already exists (or create it)
        person, person_created = Person.objects.get_or_create(nickname = context["lunchy"]["nickname"])
        # return the user_name to the final user for cross-checking
        context["lunchy"]["nickname"] = person.nickname
        context["nickname"] = context["lunchy"]["nickname"]
        logger.debug("This is the person email: " + str(person.email))
        # if no email given, raise an alert to entice user to update it to get the event notification
        if person.email == "user@domain.com":
            context["missingEmail"] = True
            return context

        # parse the datetime given by user
        avail_date = dateutil.parser.parse(context["lunchy"]["datetime"])
        # query the database to create the new availability of the user
        availability, avail_created = Availability.objects.get_or_create(
            lunch_date = avail_date,
            person = person
        )

        # try to create a lunch and a google event if enough participants
        results = handle_lunch( avail_date )
        # update context
        if results["status"] == "Lunch open":
            context["lunchCreated"] = True
        else:
            context["notEnoughGuests"] = True

        # we answered the client, so delete namespace
        del context["lunchy"]

        logger.debug("Done creating the availability with: " + str(dict({
            "nickname"  : person.nickname,
            "email"     : person.email,
            "avail_id"  : availability.id,
            "avail_date": avail_date,
            "user_created": person_created,
            "avail_created": avail_created,
            "lunch_results": results
            })))
    return context


def update_email(request):
    logger.debug("** Start updating email... **")
    # get the info from the bot
    context = request['context']
    entities = request['entities']

    # clean up previous requests by removing these keys from the context dict
    context.pop("missingEmail", None)
    context.pop("emailOk", None)

    # this function should be called within the lunchy story
    if not "lunchy" in context and "nickname" in context["lunchy"]:
        context['msg'] = "Désolé, mon robot s'est emmelé les pinceaux, pouvez-vous recommencer s'il vous plaît ?"

    # query the person object in database
    person = Person.objects.get(nickname = context["lunchy"]["nickname"])

    # update email of the person object
    from django.db import IntegrityError
    try:
        # update email of the person object
        person.email = first_entity_value(entities, 'email')
        person.save()
        context.pop("missingEmail", None)
        context["emailOk"] = True
    except IntegrityError:
        logger.info("Cannot update email %s, record already exists" % first_entity_value(entities, 'email'))
        context["emailAlreadyExists"] = True
    logger.debug("** End of updating email with context: " + str(context))
    return context

def cancel_availability(request):
    logger.debug("** Start cancelling availability... **")
    # get the info from the bot
    context = request['context']
    entities = request['entities']
    context.pop("cancelOk", None)

    # check if nickname is given, else use user_name
    nickname = first_entity_value(entities, 'contact') if entities else None
    if nickname:
        context["lunchy"]["nickname"] = nickname
    else: #no contact found, use user_name
        context["lunchy"]["nickname"] = context['user_name']

    # get user date given by user or given in a previous context
    user_date = first_entity_value(entities, 'datetime') if entities else None
    if user_date:
        context["lunchy"]["datetime"] = user_date
        # remove previous error from context
        context.pop("missingDatetime", None)
    else:
        logger.debug("No date given and context: " + str(context))
        context['missingDatetime'] = True
        return context

    # parse the datetime given by user
    avail_date = dateutil.parser.parse(context["lunchy"]["datetime"])

    try:
        # find the right availability
        avail = Availability.objects.get(person__nickname = nickname,
                lunch_date = avail_date)
        # and delete the availability
        avail_result = avail.delete()
        logger.debug("Availability deletion result: " + str(avail_result))
        # consider removing a lunch if no longer enough participants
        lunch_result = handle_lunch( avail.lunch_date )
        logger.debug("Lunch status: " + str(lunch_result))
    except Availability.DoesNotExist:
        logger.debug("Availability already deleted")
    context["cancelOk"] = True
    return context
