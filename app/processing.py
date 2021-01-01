from os import getenv
import requests

from . import models

async def alert_for_new_sample(token: str, sample: models.Sample) -> bool:
    if sample.wts:
        # dobi vse želje
        wishes_req = requests.get(
            getenv("USER_CARDS_IP") + f"/v1/wishes?card_id={sample.card_id}",
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer " + token
            })
        if wishes_req.status_code != 200:
            return False # request failed
        wishes = wishes_req.json()
        # za vsako željo pošlji message userju
        for wish in wishes:
            content = (f"User {sample.user_id} just posted a sample of card {sample.card_id} "
                + f" in a state \"{sample.state}\", contact them for more info.")
            requests.post(
                getenv("MESSAGES_IP") + "/v1/messages",
                data = f"{{\"receiver_id\": {wish['user_id']},\"content\": {content}}}",
                headers = {
                    "accept": "application/json",
                    "Authorization": "Bearer " + token
                }
            )

async def alert_for_edited_sample(token: str, sample: models.Sample):
    if sample.wts:
        # dobi vse želje
        wishes_req = requests.get(
            getenv("USER_CARDS_IP") + "/v1/wishes",
            data = {"card_id": str(sample.card_id)},
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer " + token
            })
        if wishes_req.status_code != 200:
            return False # request failed
        wishes = wishes_req.json()
        # za vsako željo pošlji message userju
        for wish in wishes:
            content = (f"User {sample.user_id} just edited a sample of card {sample.card_id} "
                + f" in a state \"{sample.state}\", contact them for more info.")
            requests.post(
                getenv("MESSAGES_IP") + "/v1/messages",
                data = f"{{\"receiver_id\": {wish['user_id']},\"content\": \"{content}\"}}",
                headers = {
                    "accept": "application/json",
                    "Authorization": "Bearer " + token
                }
            )

async def alert_for_new_wish(*args, **kwargs):
    pass

async def alert_for_edited_wish(*args, **kwargs):
    pass
