from typing import TYPE_CHECKING, Optional, Dict
from logging import getLogger
from os import environ

from .session import session_factory
from .exceptions import OrdwayClientException
from .consts import SUPPORTED_API_VERSIONS
from . import api

if TYPE_CHECKING:
    from requests import Session

logger = getLogger(__name__)


class OrdwayClient:  # pylint: disable=too-many-instance-attributes
    """ A client for interacting with Ordway's API (https://ordwaylabs.api-docs.io). """

    SUPPORTED_API_VERSIONS = SUPPORTED_API_VERSIONS

    def __init__(  # pylint: disable=too-many-arguments
        self,
        email: str,
        api_key: str,
        company: str,
        user_token: str,
        api_version: str = "1",
        sandbox: bool = False,
        proxies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        session: Optional["Session"] = None,
    ):
        self.email = email
        self.api_key = api_key
        self.company = company
        self.user_token = user_token

        self.session = session_factory(session)
        self.headers = headers
        self.proxies = proxies

        if headers is not None:
            self.session.headers.update(headers)
        if proxies is not None:
            self.session.proxies.update(proxies)

        self.api_version = api_version

        # Interfaces
        self.products = api.Products(self, sandbox=sandbox)
        self.customers = api.Customers(self, sandbox=sandbox)
        self.subscriptions = api.Subscriptions(self, sandbox=sandbox)
        self.invoices = api.Invoices(self, sandbox=sandbox)
        self.payments = api.Payments(self, sandbox=sandbox)
        self.credits = api.Credits(self, sandbox=sandbox)
        self.plans = api.Plans(self, sandbox=sandbox)
        self.refunds = api.Refunds(self, sandbox=sandbox)
        self.webhooks = api.Webhooks(self, sandbox=sandbox)
        self.journal_entries = api.JournalEntries(self, sandbox=sandbox)
        self.payment_runs = api.PaymentRuns(self, sandbox=sandbox)
        self.statements = api.Statements(self, sandbox=sandbox)
        self.coupons = api.Coupons(self, sandbox=sandbox)
        self.orders = api.Orders(self, sandbox=sandbox)
        self.usages = api.Usages(self, sandbox=sandbox)
        self.billing_runs = api.BillingRuns(self, sandbox=sandbox)
        self.revenue_schedules = api.RevenueSchedules(self, sandbox=sandbox)
        self.billing_schedules = api.BillingSchedules(self, sandbox=sandbox)
        self.revenue_rules = api.RevenueRules(self, sandbox=sandbox)
        self.chart_of_accounts = api.ChartOfAccounts(self, sandbox=sandbox)

    @property
    def api_version(self):
        """ The currently used API version """

        return self._api_version

    @api_version.setter
    def api_version(self, api_version):
        if api_version.startswith("v"):
            api_version = api_version[1:]

        self._api_version = api_version
        self._verify_api_version()

    def _verify_api_version(self) -> None:
        """ Verifies that the requested API version is supported by OrdwayClient. """

        version = self.api_version

        if version not in self.SUPPORTED_API_VERSIONS:
            raise OrdwayClientException(
                f'OrdwayClient does not currently support the API version "v{version}".'
            )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    @classmethod
    def from_env(cls) -> "OrdwayClient":
        """ Instantiates `OrdwayClient` using environment variables. """

        try:
            env_vars = {
                "email": environ["ORDWAY_EMAIL"],
                "api_key": environ["ORDWAY_API_KEY"],
                "company": environ["ORDWAY_COMPANY"],
                "user_token": environ["ORDWAY_USER_TOKEN"],
            }

            logger.debug(
                'Instantiating client from environment with email "%s" and company "%s".',
                env_vars["email"],
                env_vars["company"],
            )
        except KeyError as err:
            err_message = (
                "Cannot instantiate `OrdwayClient` with `.from_env`."
                "Must set all of the following env vars: `ORDWAY_EMAIL`, `ORDWAY_API_KEY`,"
                "`ORDWAY_COMPANY`, and `ORDWAY_USER_TOKEN`."
            )

            logger.error(err_message)

            raise OrdwayClientException(err_message) from err

        api_version = environ.get("ORDWAY_API_VERSION")

        if api_version is not None:
            env_vars["api_version"] = api_version

        # MyPy complains about incompatible type. Argument 1 to "OrdwayClient" has incompatible type "**Dict[str, str]"; expected "Optional[Dict[str, str]]"
        return cls(**env_vars)  # type: ignore
