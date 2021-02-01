from ayesaac.services.common import run_service_wrapper

from .external_interface import ExternalInterface


if __name__ == "__main__":
    run_service_wrapper(ExternalInterface)
