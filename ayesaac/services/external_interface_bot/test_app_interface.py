import asyncio

from ayesaac.services.external_interface_bot.bot import AppInterface
from ayesaac.services_lib.queues.queue_manager import QueueManager
from threading import Thread


def test_queue_consumption():
    """
    Requires rabbitmq service to be running, as this uses the real queue system.
    Run with Pytest.
    """

    app_interface = AppInterface(test_run=True)
    # the queue consuming run methods are blocking until they receive a message
    # and have no way of exiting - in other words, they are daemons
    app_thread = Thread(target=app_interface.run, daemon=True)
    app_thread.start()
    test_queue_manager = QueueManager(["AppInterface"])

    test_queue_manager.publish("AppInterface", {"test": "test"})

    loop = asyncio.get_event_loop()
    # let the message be processed
    loop.run_until_complete(asyncio.sleep(0.5))
    loop.close()

    assert app_interface.single_result_cache
    print(app_interface.single_result_cache)
