import os
from enum import Enum
from typing import Any, Dict, Literal, Optional, Type

from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field
from scrapeless.client import Scrapeless as ScrapelessClient

from langchain_scrapeless.error_messages import ERROR_SCRAPELESS_TOKEN_ENV_VAR_NOT_SET
from langchain_scrapeless.utils import create_scrapeless_client
from langchain_scrapeless.wrappers import (
    ScrapelessDeepSerpAPIWrapper,
)


class CategoryEnum(str, Enum):
    all_categories = "0"
    arts_entertainment = "3"
    computers_electronics = "5"
    finance = "7"
    games = "8"
    home_garden = "11"
    business_industrial = "12"
    internet_telecom = "13"
    people_society = "14"
    news = "16"
    shopping = "18"
    law_government = "19"
    sports = "20"
    books_literature = "22"
    performing_arts = "23"
    visual_art_design = "24"
    advertising_marketing = "25"
    office_services = "28"
    real_estate = "29"
    computer_hardware = "30"
    programming = "31"
    software = "32"
    offbeat = "33"
    movies = "34"
    music_audio = "35"
    tv_video = "36"
    banking = "37"
    insurance = "38"
    card_games = "39"
    computer_video_games = "41"
    jazz = "42"
    online_goodies = "43"
    beauty_fitness = "44"
    health = "45"
    agriculture_forestry = "46"
    autos_vehicles = "47"
    construction_maintenance = "48"
    manufacturing = "49"
    transportation_logistics = "50"
    web_hosting_domain_registration = "53"
    social_issues_advocacy = "54"
    dating_personals = "55"
    ethnic_identity_groups = "56"
    charity_philanthropy = "57"
    parenting = "58"
    religion_belief = "59"
    jobs = "60"
    classifieds = "61"
    weather = "63"
    antiques_collectibles = "64"
    hobbies_leisure = "65"
    pets_animals = "66"
    travel = "67"
    apparel = "68"
    consumer_resources = "69"
    gifts_special_event_items = "70"
    food_drink = "71"
    mass_merchants_department_stores = "73"
    education = "74"
    legal = "75"
    government = "76"
    enterprise_technology = "77"
    consumer_electronics = "78"
    environmental_issues = "82"
    marketing_services = "83"
    seo_marketing = "84"
    vehicle_parts_accessories = "89"
    stereo_systems_components = "91"
    skin_nail_care = "93"
    fitness = "94"
    office_supplies = "95"
    real_estate_agencies = "96"
    consumer_advocacy_protection = "97"
    fashion_designers_collections = "98"
    gifts_2 = "99"
    cards_greetings = "100"
    spirituality = "101"
    personals = "102"
    isps = "104"
    online_games = "105"
    investing = "107"
    language_resources = "108"
    broadcast_network_news = "112"
    gay_lesbian_bisexual_transgender = "113"
    baby_care_hygiene = "115"
    water_sports = "118"
    wildlife = "119"
    cookware_diningware = "120"
    grocery_food_retailers = "121"
    cooking_recipes = "122"
    tobacco_products = "123"
    clothing_accessories = "124"
    homemaking_interior_decor = "137"
    vehicle_maintenance = "138"
    face_body_care = "143"
    unwanted_body_facial_hair_removal = "144"
    spas_beauty_services = "145"
    hair_care = "146"
    cosmetology_beauty_professionals = "147"
    off_road_vehicles = "148"
    kids_teens = "154"
    human_resources = "157"
    home_improvement = "158"
    public_safety = "166"
    emergency_services = "168"
    vehicle_licensing_registration = "170"


class ScrapelessGoogleTrendsInput(BaseModel):
    """Input for Scrapeless DeepSerp Google Trends tool."""

    q: str = Field(
        description="""
        Parameter defines the query or queries you want to search.

        You can use anything that you would use in a regular Google Trends search.
        
        - The maximum number of queries per search is **5**.
          (This only applies to `interest_over_time` and `compared_breakdown_by_region` 
            data types.)
        - Other types of data will only accept **1 query** per search.
        """
    )
    data_type: Optional[
        Literal[
            "autocomplete",
            "interest_over_time",
            "compared_breakdown_by_region",
            "interest_by_subregion",
            "related_queries",
            "related_topics",
        ]
    ] = Field(
        default="interest_over_time",
        description="""
        The supported types are:
            - autocomplete
            - interest_over_time
            - compared_breakdown_by_region
            - interest_by_subregion
            - related_queries
            - related_topics
        """,
    )

    date: Optional[str] = Field(
        default="today 1-m",
        description="""
        The supported dates are:
            now 1-H, now 4-H, now 1-d, now 7-d,
            today 1-m, today 3-m, today 12-m, today 5-y, all.
        
        You can also pass custom values:
        
        - Dates from 2004 to present:
            yyyy-mm-dd yyyy-mm-dd
            e.g. 2021-10-15 2022-05-25
        
        - Dates with hours within a week range:
            yyyy-mm-ddThh yyyy-mm-ddThh
            e.g. 2022-05-19T10 2022-05-24T22
            (Hours will be calculated depending on the tz (time zone) parameter.)
        """,
    )

    hl: Optional[str] = Field(
        default="en",
        description="""
        Parameter defines the language to use for the Google Trends search. 
        It's a two-letter language code. 
            (e.g., en for English, es for Spanish, or fr for French).
        """,
    )

    tz: Optional[str] = Field(
        default="420", description="Time zone offset. Default is 420."
    )

    geo: Optional[
        Literal[
            "",
            "AR",
            "AU",
            "AT",
            "BE",
            "BR",
            "CA",
            "CL",
            "CO",
            "CZ",
            "DK",
            "EG",
            "FI",
            "FR",
            "DE",
            "GR",
            "HK",
            "HU",
            "IN",
            "ID",
            "IE",
            "IL",
            "IT",
            "JP",
            "KE",
            "MY",
            "MX",
            "NL",
            "NZ",
            "NG",
            "NO",
            "PE",
            "PH",
            "PL",
            "PT",
            "RO",
            "RU",
            "SA",
            "SG",
            "ZA",
            "KR",
            "ES",
            "SE",
            "CH",
            "TW",
            "TH",
            "TR",
            "UA",
            "GB",
            "US",
            "VN",
        ]
    ] = Field(
        default=None,
        description="""
        Parameter defines the location from where you want the search to originate. 
        It defaults to Worldwide 
            (activated when the value of geo parameter is not set or empty).
        """,
    )

    cat: Optional[CategoryEnum] = Field(
        default=CategoryEnum.all_categories,
        description=(
            "Parameter is used to define a search category. "
            "The default value is set to '0' (All categories)."
        ),
    )


class ScrapelessDeepSerpGoogleTrendsTool(BaseTool):
    """Tool that runs Scrapeless DeepSerp Google Trends API.

    To use, you should have the environment variable `SCRAPELESS_API_KEY` set
    with your API key, or pass `scrapeless_api_key`
    as a named parameter to the constructor.

    For details, see  https://docs.apify.com/platform/integrations/langchain

    Example:
      .. code-block:: python

        from langchain_openai import ChatOpenAI
        from langchain_scrapeless import ScrapelessDeepSerpGoogleTrendsTool
        from langgraph.prebuilt import create_react_agent

        llm = ChatOpenAI()

        tool = ScrapelessDeepSerpGoogleTrendsTool()

        # Use the tool with an agent
        tools = [tool]
        agent = create_react_agent(llm, tools)

        for chunk in agent.stream(
                {"messages": [("human", "I want to know the trends of AI")]},
                stream_mode="values"
        ):
            chunk["messages"][-1].pretty_print()
        )


    """

    name: str = "scrapeless_deepserp_google_trends"
    description: str = """
        Get trending search data from Google Trends.

        Restrictions:
            Activated for queries about trends, popularity, or interest over time.
        
        Valid:
            Find the search interest for "AI" over the last year.
        
        Invalid:
            A general question like "What is AI?" (use google_search).
    """

    args_schema: Type[BaseModel] = ScrapelessGoogleTrendsInput
    handle_tool_error: bool = True

    scrapeless_deepserp_api_wrapper: ScrapelessDeepSerpAPIWrapper = Field(
        default_factory=ScrapelessDeepSerpAPIWrapper
    )

    def __int__(self, scrapeless_api_key: str | None = None, **kwargs: Any) -> None:
        """Initialize the ScrapelessDeepSerpGoogleTrendsTool.

        Args:
            scrapeless_api_key: The API key for the Scrapeless API.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If the `SCRAPELESS_API_KEY` environment variable is not set.
        """

        scrapeless_api_key = scrapeless_api_key or os.getenv("SCRAPELESS_API_KEY")
        if not scrapeless_api_key:
            msg = ERROR_SCRAPELESS_TOKEN_ENV_VAR_NOT_SET
            raise ValueError(msg)

        scrapeless_client = create_scrapeless_client(
            ScrapelessClient, scrapeless_api_key
        )

        if "scrapeless_api_key" in kwargs:
            kwargs["scrapeless_deepserp_api_wrapper"] = ScrapelessDeepSerpAPIWrapper(
                scrapeless_api_key=scrapeless_api_key,
                scrapeless_client=scrapeless_client,
            )

        super().__init__(**kwargs)

    def _run(
        self,
        q: str,
        data_type: Optional[
            Literal[
                "autocomplete",
                "interest_over_time",
                "compared_breakdown_by_region",
                "interest_by_subregion",
                "related_queries",
                "related_topics",
            ]
        ] = "interest_over_time",
        date: Optional[str] = "today 1-m",
        hl: Optional[str] = "en",
        tz: Optional[str] = "420",
        geo: Optional[str] = None,
        cat: Optional[CategoryEnum] = CategoryEnum.all_categories,
    ) -> Dict[str, Any]:
        """Execute the Scrapeless DeepSerp Google Trends API."""

        try:
            results = self.scrapeless_deepserp_api_wrapper.get_google_trends_results(
                q=q,
                data_type=data_type,
                date=date,
                hl=hl,
                tz=tz,
                geo=geo,
                cat=cat,
            )
            return results

        except Exception as e:
            if isinstance(e, ToolException):
                raise e
            raise ValueError(
                f"An error occurred while scraping the query {q}: {str(e)}"
            )
