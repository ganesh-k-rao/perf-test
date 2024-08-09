import asyncio
import random
import time

import aiohttp
from aiohttp.client_exceptions import ServerTimeoutError

from request_payload import api_ticket

API_BASE_URL = "https://tlc.staging.int.urbinternal.com/"  # staging "https://tlc.staging.int.urbinternal.com/"  # Integration "https://tlc.integ.int.urbinternal.com/"
API_ENDPOINT = "api/v1/ticket"


async def main():

    BATCH_SIZE = 100
    TOTAL_TICKETS = 500
    UNQ_TICKET_ID = "V1_AUG03_"
    try:
        total_timeout = aiohttp.client.ClientTimeout(total=200)
        async with aiohttp.ClientSession(timeout=total_timeout) as session:
            start_time_all_tasks = time.time()
            all_results = []
            for batch in range(0, TOTAL_TICKETS, BATCH_SIZE):
                tasklist = []
                for i in range(0, BATCH_SIZE):
                    ticket_id = UNQ_TICKET_ID + str(random.randint(1, 5000))
                    tasklist.append(
                        asyncio.create_task(request_api(session, "POST", ticket_id))
                    )
                start_time = time.time()
                results = await asyncio.gather(*tasklist)
                time_taken = (time.time() - start_time) * 1000
                all_results.extend(results)
                print(f"Time taken to ingest ticket: {round(time_taken, 2)} \n")
                tasklist = []
                await asyncio.sleep(10)

            time_taken_all_tasks = (time.time() - start_time_all_tasks) * 1000
            print(
                f"Time taken to ingest ticket all tickets: {round(time_taken_all_tasks,2)}"
            )
            with open("results.txt", "a") as f:
                for data in all_results:
                    f.write(data)
                    f.write("\n")
                f.write("=======================================================")
                f.write("***************** End of Batch****************************")
                f.write("=======================================================")
    except Exception as e:
        print("Error with request: " + str(e))


async def request_api(session, method, ticket_id):
    api_ticket.get("dig_ticket")["ticket_id"] = ticket_id
    try:
        async with session.post(
            f"{API_BASE_URL}{API_ENDPOINT}", json=api_ticket
        ) as response:
            result = await response.text()
            return result + " | " + ticket_id
    except ServerTimeoutError as e:
        print(f"Server timeout error for ticket: {ticket_id} \n exception: {e}")
    except Exception as e:
        print(f"Unhandled exception for ticket: {ticket_id} \n exception: {e}")


asyncio.run(main())
