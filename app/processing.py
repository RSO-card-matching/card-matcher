from os import getenv
from multiprocessing import Process
import requests

from . import models, main

def alert_separately_sample(sample: models.Sample, message: str) -> None:
    if sample.wts:
        token = main.create_system_token()
        # dobi vse želje
        wishes_req = requests.get(
            getenv("USER_CARDS_IP") + f"/v1/wishes?card_id={sample.card_id}",
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer " + token
            })
        if wishes_req.status_code != 200:
            return # request failed
        wishes = wishes_req.json()
        # za vsako željo pošlji message userju
        for wish in wishes:
            requests.post(
                getenv("MESSAGES_IP") + "/v1/messages",
                data = f"{{\"receiver_id\": {wish['user_id']},\"content\": \"{message}\"}}".encode('utf-8'),
                headers = {
                    "accept": "application/json",
                    "Authorization": "Bearer " + token
                }
            )

async def alert_for_new_sample(sample: models.Sample) -> None:
    p = Process(
        target = alert_separately_sample,
        args = (
            sample,
            f"User {sample.user_id} just posted a sample of card {sample.card_id} "
                + f"in a state \\\"{sample.state}\\\", contact them for more info."
        )
    )
    p.start()

async def alert_for_edited_sample(sample: models.Sample) -> None:
    p = Process(
        target = alert_separately_sample,
        args = (
            sample,
            f"User {sample.user_id} just edited a sample of card {sample.card_id} "
                + f"in a state \\\"{sample.state}\\\", contact them for more info."
        )
    )
    p.start()

def alert_separately_wish(wish: models.Wish, message) -> None:
    token = main.create_system_token()
    # dobi vse primerke
    samples_req = requests.get(
        getenv("USER_CARDS_IP") + f"/v1/samples?card_id={wish.card_id}",
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + token
        })
    if samples_req.status_code != 200:
        return # request failed
    samples = samples_req.json()
    # za vsako željo pošlji message userju
    for sample in samples:
        requests.post(
            getenv("MESSAGES_IP") + "/v1/messages",
            data = f"{{\"receiver_id\": {wish.user_id},\"content\": \"{message(sample)}\"}}".encode('utf-8'),
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer " + token
            }
        )

async def alert_for_new_wish(wish: models.Wish):
    p = Process(
        target = alert_separately_wish,
        args = (
            wish,
            lambda sample: f"User {sample['user_id']} has a sample of card {sample['card_id']} "
                + f"in a state \\\"{sample['state']}\\\", contact them for more info."
        )
    )
    p.start()

async def alert_for_edited_wish(wish: models.Wish):
    p = Process(
        target = alert_separately_wish,
        args = (
            wish,
            lambda sample: f"User {sample['user_id']} has a sample of card {sample['card_id']} "
                + f"in a state \\\"{sample['state']}\\\", contact them for more info."
        )
    )
    p.start()
