# Documentation



# Getting Started



The Whitepages API provides access to comprehensive person and property data. Whether you're verifying identities, enriching customer records, or researching properties, our API delivers the data you need.

## Get Your API Key

To access the API, you'll need an API key. Sign up for a **free trial** at [whitepages.com/pro-api](https://www.whitepages.com/pro-api).

<Callout type="warn" title="Keep Your API Key Secret">
  Your API key authenticates all requests and tracks usage for billing. Never
  expose it in client-side code or public repositories. If your key is
  compromised, contact [support@whitepages.com](mailto:support@whitepages.com)
  for a replacement.
</Callout>

## Available APIs

<Cards>
  <Card title="Person Search" href="/documentation/person-search" description="Look up individuals by name, phone, or address" />

  <Card title="Property Search" href="/documentation/property-search" description="Get ownership and resident data for any address" />
</Cards>

## Making Requests

All API requests require your API key in the `X-Api-Key` header:

```bash
curl 'https://api.whitepages.com/v1/person?name=John%20Smith' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

Responses are returned in JSON format. Each successful request that returns data consumes one billable query.

## Next Steps

Ready to make your first API call? Start with the [Person Search](/documentation/person-search) tutorial.


# Getting a Trial API Key















This guide walks you through the process of signing up for a free trial API key. The trial gives you access to all API endpoints so you can evaluate the service before committing to a paid plan.

## Step 1: Visit the API Page

Go to [whitepages.com/pro-api](https://www.whitepages.com/pro-api) to access the API signup page.

<img alt="API Landing Page" src={__img0} placeholder="blur" />

You'll see the "Get API Access" form on the right side of the page.

## Step 2: Enter Your Contact Information

The first form requires three pieces of information:

* **Full Name** - Your full name
* **Business Email Address** - A valid business email address (required for trial approval)
* **Phone Number** - Your phone number in the format (555) 555-5555

<img alt="Signup Form" src={__img1} placeholder="blur" />

Fill in your details and click the **Start for Free** button.

<img alt="Form Filled" src={__img2} placeholder="blur" />

<Callout type="info" title="Use a Business Email">
  Using a business email address (e.g., [yourname@company.com](mailto:yourname@company.com)) rather than a
  personal email increases your chances of trial approval and faster processing.
</Callout>

## Step 3: Provide API Usage Details

After submitting your contact information, you'll be asked to provide more details about your API needs:

<img alt="Second Form Stage" src={__img3} placeholder="blur" />

Fill out the following fields:

* **Anticipated Monthly API Calls** - Select your expected usage volume
* **Do you have a technical resource for implementation?** - Indicate if you have development resources
* **Who is the end user for the data?** - Select who will be using the data (Internal Staff, Businesses you serve, Consumers, or Other)
* **Briefly describe how you plan to use the API** - Provide a short description of your use case

<img alt="Second Form Filled" src={__img4} placeholder="blur" />

Click **Access API Trial** to submit your request.

<Callout type="info" title="No Credit Card Required">
  The trial signup does not require a credit card. You can evaluate the API
  completely free during the trial period.
</Callout>

## Step 4: Check Your Email

After submitting the form, you'll see a confirmation message:

<img alt="Confirmation" src={__img5} placeholder="blur" />

Check your email for instructions on how to activate your trial key.

## Step 5: Start Using Your API Key

Once you receive your API key, you can start making requests immediately. Include your key in the `X-Api-Key` header:

```bash
curl 'https://api.whitepages.com/v1/person?name=John%20Smith' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<Callout type="warn" title="Keep Your API Key Secure">
  Never share your API key publicly or commit it to version control. If your key
  is compromised, contact
  [support@whitepages.com](mailto:support@whitepages.com) immediately.
</Callout>

## Trial Limitations

The trial API key includes:

* Access to all API endpoints
* Limited number of queries for evaluation purposes
* Full response data (no field restrictions)

For production use or higher query volumes, visit the [API Pricing](https://www.whitepages.com/pro-api/pricing) page.

## Next Steps

<Cards>
  <Card title="Person Search" href="/documentation/person-search" description="Learn how to search for individuals" />

  <Card title="Property Search" href="/documentation/property-search" description="Look up property ownership data" />
</Cards>


# Guides



In-depth guides for integrating and using the Whitepages API.

<Callout type="info" title="Coming Soon">
  Detailed guides are under development.
</Callout>


# Property Search



The Property Search API returns ownership and resident information for a given property. Use it to identify property owners, find current residents, or verify property details.

<Callout type="info">
  **V2 API Available**: We recommend using the [V2 Property
  API](/references/property-v2/search_property_v2) for new integrations. The V2
  API provides improved data structure and additional features.
</Callout>

## Make Your First Request

<Steps>
  <Step>
    ### Send a Request

    Search for property details by address using the V2 API:

    ```bash title="Request"
    curl 'https://api.whitepages.com/v2/property/?street=1600%20Pennsylvania%20Ave%20NW&city=Washington&state_code=DC' \
      --header 'X-Api-Key: YOUR_API_KEY'
    ```

    Replace `YOUR_API_KEY` with your actual API key.
  </Step>

  <Step>
    ### Review the Response

    A successful request returns property details with owner and resident information:

    ```json title="Response"
    {
      "result": {
        "property_id": "RVMKL8l80mK",
        "apn": "0187-S000-0802",
        "property_address": {
          "full_address": "1600 Pennsylvania Ave NW Washington, DC 20500",
          "line1": "1600 Pennsylvania Ave NW",
          "city": "Washington",
          "state": "DC",
          "zip": "20500",
          "house": "1600",
          "street": "Pennsylvania",
          "street_type": "Ave",
          "county": "District of Columbia"
        },
        "mailing_address": {
          "full_address": "1600 Pennsylvania Ave NW Washington, DC 20500",
          "line1": "1600 Pennsylvania Ave NW",
          "city": "Washington",
          "state": "DC",
          "zip": "20500",
          "house": "1600",
          "street": "Pennsylvania",
          "street_type": "Ave",
          "county": "District of Columbia"
        },
        "geolocation": {
          "lat": 38.897697,
          "lng": -77.034392
        },
        "ownership_info": {
          "owner_type": "Business",
          "business_owners": [
            {
              "name": "United States Of America"
            }
          ],
          "person_owners": [
            {
              "id": "PX3vr2aM2E3",
              "name": "Donald Duck",
              "current_addresses": [
                {
                  "full_address": "1600 Pennsylvania Ave NW # 666 Washington, DC 20500"
                }
              ],
              "phones": [
                {
                  "number": "12015215520",
                  "type": "Landline"
                }
              ],
              "emails": [
                {
                  "email": "sample.email@gmail.com"
                }
              ]
            }
          ]
        },
        "residents": [
          {
            "id": "PX3vr2aM2E3",
            "name": "Donald Duck",
            "current_addresses": [
              {
                "full_address": "1600 Pennsylvania Ave NW # 666 Washington, DC 20500"
              }
            ],
            "phones": [
              {
                "number": "12015215520",
                "type": "Landline"
              }
            ],
            "emails": [
              {
                "email": "sample.email@gmail.com"
              }
            ]
          }
        ]
      }
    }
    ```

    The response includes the verified property with geolocation, property owners, and current residents.
  </Step>
</Steps>

## Request Parameters

| Parameter    | Required | Description           | Example                    |
| ------------ | -------- | --------------------- | -------------------------- |
| `street`     | No\*     | Street address        | `1600 Pennsylvania Ave NW` |
| `city`       | No\*     | City name             | `Washington`               |
| `state_code` | No\*     | Two-letter state code | `DC`                       |
| `zipcode`    | No\*     | ZIP code              | `20500`                    |

<Callout>
  At least one parameter is required. Include multiple parameters for more
  precise results.
</Callout>

**Example with ZIP code:**

```
https://api.whitepages.com/v2/property/?street=1600%20Pennsylvania%20Ave%20NW&zipcode=20500
```

**Example by property ID:**

```
https://api.whitepages.com/v2/property/RVMKL8l80mK
```

## What's Next

You've completed the getting started tutorials. Explore the [References](/references) section for complete API documentation.


# Purchasing the API









This guide walks you through the process of purchasing a paid Whitepages Pro API subscription. Paid plans offer higher query limits and are suitable for production use.

## Step 1: Visit the Pricing Page

Go to [whitepages.com/pro-api/pricing](https://www.whitepages.com/pro-api/pricing) to view available plans.

<img alt="Pricing Page" src={__img0} placeholder="blur" />

You'll see three options:

* **14-Day Trial** - Free access with 50 queries to evaluate the API
* **Pro API Plan** - Paid plans with 1,000 to 30,000 queries per month
* **Higher-Volume Plans** - Enterprise plans for 50,000+ queries per month

## Step 2: Select Your Plan

### Monthly vs Annual Billing

Use the toggle at the top to switch between **Monthly** and **Annual** billing. Annual plans offer a 15% discount.

### Choose Your Query Volume

For the Pro API Plan, select your monthly query volume from the dropdown. Options range from 1,000 to 30,000 queries per month.

Click **Get Pro Access** to proceed to checkout.

<Callout type="info" title="Need More Queries?">
  For volumes above 30,000 queries per month, select "Higher-Volume Plans" and
  [schedule a
  meeting](https://www.getclockwise.com/c/ewang-whitepages-com/quick-meeting)
  with our sales team.
</Callout>

## Step 3: Complete the Checkout Form

After clicking "Get Pro Access", you'll be taken to the secure checkout page.

<img alt="Checkout Page" src={__img1} placeholder="blur" />

### Account Details

Fill in the following information:

* **Email Address** - Your business email where the API key will be sent
* **Company Name** - Your company or organization name

<Callout type="warn" title="Existing Whitepages Customers">
  If you already have a Whitepages consumer account, you must use a different
  email address for your API account. You can either use a separate business
  email or add `+api` to your existing email (e.g., `yourname+api@company.com`)
  to create a new API account.
</Callout>

* **Company Address** - Your business address - **Use Case** - Select how you
  plan to use the API: - Contact Enrichment - Identity Verification - Reverse
  Phone Lookup - Property & Owner Research - Other - **Phone** - Your contact
  phone number

<Callout type="info" title="Double-Check Your Email">
  Your account confirmation and billing receipts will be sent to this email
  address. Make sure it's correct before submitting.
</Callout>

### Payment Information

Enter your payment details:

* **Cardholder Name** - Name as it appears on your card
* **Card Number** - Your credit card number (Visa, Mastercard, American Express, or Discover accepted)
* **Expiration Date** - Card expiration month and year
* **CVV** - The 3 or 4 digit security code on your card
* **Billing ZIP Code** - The ZIP code associated with your billing address

<img alt="Checkout Form Filled" src={__img2} placeholder="blur" />

## Step 4: Review and Submit

Before submitting, review your order summary on the right side of the page:

* Verify the plan name and query volume
* Check the monthly price
* Note that sales tax may be added based on your location

Check the box to agree to the recurring charges, then click **Submit Order**.

<Callout type="info" title="Cancel Anytime">
  You can cancel your subscription at any time by contacting Whitepages customer
  support. There are no long-term contracts for monthly plans.
</Callout>

## Step 5: Copy Your API Key

After successful payment, your API key will be displayed on the confirmation screen.

<Callout type="warn" title="Save Your API Key Immediately">
  Your API key is only shown once after purchase. Copy it immediately and store
  it in a secure location such as a password manager or secrets vault. You will
  not receive your API key via email.
</Callout>

## Using Your API Key

Include your API key in the `X-Api-Key` header with every request:

```bash
curl 'https://api.whitepages.com/v1/person?name=John%20Smith' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<Callout type="warn" title="Keep Your API Key Secure">
  Never share your API key publicly or commit it to version control. If your key
  is compromised, contact
  [support@whitepages.com](mailto:support@whitepages.com) immediately.
</Callout>

## Managing Your Subscription

To manage your subscription, upgrade your plan, or view usage statistics:

1. Log in at [whitepages.com/auth/login](https://www.whitepages.com/auth/login)
2. Navigate to your account dashboard
3. View billing history and current usage

For billing questions or to cancel your subscription, contact customer support at (800) 916-7806 or visit [support.whitepages.com](https://support.whitepages.com/hc/en-us).

## Next Steps

<Cards>
  <Card title="Getting Started" href="/documentation/getting-started" description="Learn how to make your first API request" />

  <Card title="Person Search" href="/documentation/person-search" description="Search for individuals by name, phone, or address" />
</Cards>


# Authentication



import { Callout } from "fumadocs-ui/components/callout";

All API requests require a valid API key provided in the `X-Api-Key` header.

## API Key

Include your API key in every request using the `X-Api-Key` header:

```bash
curl -X GET "https://api.whitepages.com/v1/person/" \
  -H "X-Api-Key: your-api-key-here"
```

<Callout type="warn">
  Keep your API key secure. Do not expose it in client-side code or public
  repositories.
</Callout>

## Obtaining an API Key

Contact our support team at [support@whitepages.com](mailto:support@whitepages.com) for API key provisioning and management.

## Error Responses

If authentication fails, you will receive a `403 Forbidden` response:

```json
{
  "message": "Forbidden"
}
```

Common causes for authentication errors:

* Missing `X-Api-Key` header
* Invalid or revoked API key
* API key not authorized for the requested endpoint


# Billing



import { Callout } from "fumadocs-ui/components/callout";

API usage is tracked and billed based on successful requests.

## Billing Rules

| Response Type      | Billable |
| ------------------ | -------- |
| 2xx (Success)      | Yes      |
| 4xx (Client Error) | Yes      |
| 5xx (Server Error) | No       |
| 429 (Rate Limit)   | No       |

<Callout type="info">
  Only requests to Person and Property endpoints are charged. Account endpoints
  are not billable.
</Callout>

## Billable Requests

All `2xx` (success) and `4xx` (client error) responses from Person and Property endpoints are charged to your account.

## Non-Billable Requests

The following responses are **not** charged:

* `5xx` (server error) responses - issues on our end
* `429` (rate limit) responses - when you've exceeded rate limits

## Billing Period

Usage is calculated from the start of the month in UTC time. Your billing cycle resets on the 1st of each month at 00:00 UTC.

## Usage Reports

Detailed usage reports are available through the [Account Usage](/references/account/get_account_usage_data) endpoint. You can query:

* Daily request counts
* Usage over custom date ranges (up to 90 days)
* Total requests for a time period

## Support

For billing inquiries, quota adjustments, or plan changes, please contact our team at [support@whitepages.com](mailto:support@whitepages.com).


# Routes



import { Cards, Card } from "fumadocs-ui/components/card";

The Whitepages API provides comprehensive access to person and property data with enterprise-grade authentication and usage tracking.

Before using the API, review the [Authentication](/references/authentication), [Rate Limits](/references/rate-limits), and [Billing](/references/billing) documentation.

## Account API

Account management endpoints for retrieving usage statistics.

<Cards>
  <Card title="Retrieve usage data for a specific time range" description="Retrieve API usage data for a specified date range." href="/references/account/get_account_usage_data" />
</Cards>

## Person API

Search for individuals by name, phone number, and address.

<Cards>
  <Card title="Search for a person by name, phone number, and address" description="Retrieve person information based on the provided query parameters." href="/references/person/search_person_by_name_phone_or_address" />

  <Card title="Gets person details by id" description="Retrieve detailed person information by Whitepages person ID." href="/references/person/get_person_by_id" />
</Cards>

## Property V2 API

<Cards>
  <Card title="Get property by ID" description="Retrieve property information by property ID." href="/references/property-v2/get_property_by_id_v2" />

  <Card title="Search for property by address" description="Search for property by address parameters." href="/references/property-v2/search_property_v2" />
</Cards>


# Python SDK



import { Callout } from "fumadocs-ui/components/callout";

<Callout type="info">
  The Python SDK is coming soon.
</Callout>


# Rate Limits



import { Callout } from "fumadocs-ui/components/callout";

API usage is rate-limited to ensure system stability and fair usage across all customers.

## Rate Limit Behavior

When you exceed the rate limit, the API returns a `429 Too Many Requests` status code with retry information.

```json
{
  "message": "Too Many Requests"
}
```

<Callout type="info">
  When you receive a 429 response, wait before retrying your request. Implement
  exponential backoff in your application for best results.
</Callout>

## Monthly Query Limits

Your API plan includes a monthly query limit. When exceeded, you will receive:

```json
{
  "message": "Limit Exceeded"
}
```

This indicates you have hit your monthly query limit. You can either:

* Wait until the next month when your limit resets
* Contact support for additional queries or a plan upgrade

## Best Practices

* **Implement retry logic** with exponential backoff for 429 responses
* **Cache responses** when appropriate to reduce API calls
* **Monitor usage** via the [Account Usage](/references/account/get_account_usage_data) endpoint
* **Batch requests** where possible to optimize your quota

## Rate Limit Increases

For rate limit increases or quota adjustments, please contact our team at [support@whitepages.com](mailto:support@whitepages.com).


# TypeScript SDK



import { Callout } from "fumadocs-ui/components/callout";

<Callout type="info">
  The TypeScript SDK is coming soon.
</Callout>


# Filter by Age Range



Use the `min_age` and `max_age` parameters to filter person search results by age range. This is useful when you need to find individuals within a specific age bracket.

## Basic Usage

Add `min_age` and/or `max_age` to your request to filter results:

```bash title="Request"
curl 'https://api.whitepages.com/v1/person?name=John%20Smith&min_age=25&max_age=45' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

This returns only records for individuals between 25 and 45 years old.

## Parameters

| Parameter | Type    | Description                            |
| --------- | ------- | -------------------------------------- |
| `min_age` | integer | Minimum age (inclusive). Must be 18-65 |
| `max_age` | integer | Maximum age (inclusive). Must be 18-65 |

<Callout type="warn" title="Age Range Limits">
  Age filters are restricted to individuals between 18 and 65 years old. Values
  outside this range will return an error.
</Callout>

## Examples

### Filter by Minimum Age

Filter for individuals 21 years or older:

```bash
curl 'https://api.whitepages.com/v1/person?name=Jane%20Doe&city=Chicago&state_code=IL&min_age=21' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Filter by Maximum Age

Filter for individuals 40 or younger:

```bash
curl 'https://api.whitepages.com/v1/person?last_name=Johnson&state_code=FL&max_age=40' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Filter by Age Range

Filter for individuals between 25 and 55:

```bash
curl 'https://api.whitepages.com/v1/person?name=Michael%20Williams&zipcode=90210&min_age=25&max_age=55' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

## Combining with Other Filters

Age filters work alongside all other person search parameters:

```bash
curl 'https://api.whitepages.com/v1/person?first_name=Sarah&last_name=Miller&city=Seattle&state_code=WA&min_age=30&max_age=50' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<Callout type="info" title="Age Data Availability">
  Age filtering relies on available data. Some records may not have age
  information and will be excluded from filtered results.
</Callout>

## Response

The response format remains the same as a standard person search. Age filters only affect which records are returned, not the structure of the response.

```json title="Response"
[
  {
    "id": "P1234567890",
    "name": "John Smith",
    "aliases": ["Johnny Smith"],
    "is_dead": false,
    "current_addresses": [
      { "id": "A9876543210", "address": "456 Oak Ave, Chicago, IL 60601" }
    ],
    "historic_addresses": [
      { "id": "A1234567890", "address": "789 Pine St, Chicago, IL 60602" }
    ],
    "owned_properties": [],
    "phones": [{ "number": "(312) 555-0123", "type": "mobile", "score": 88 }],
    "emails": ["jsmith@example.com"],
    "date_of_birth": "1992-07-22",
    "linkedin_url": "https://linkedin.com/in/jsmith",
    "company_name": "Tech Solutions Inc",
    "job_title": "Product Manager",
    "relatives": [{ "id": "P0987654321", "name": "Mary Smith" }]
  }
]
```


# Person Search



The Person Search API finds matching records in the Whitepages dataset based on name, location, phone number, or address. Use it to verify identities, find contact information, or enrich customer data.

## Make Your First Request

<Steps>
  <Step>
    ### Send a Request

    Search for a person by name and location:

    ```bash title="Request"
    curl 'https://api.whitepages.com/v1/person?name=John%20Smith&city=New%20York&state_code=NY' \
      --header 'X-Api-Key: YOUR_API_KEY'
    ```

    Replace `YOUR_API_KEY` with your actual API key.
  </Step>

  <Step>
    ### Review the Response

    A successful request returns matching person records:

    ```json title="Response"
    [
      {
        "id": "P1234567890",
        "name": "John Smith",
        "aliases": ["Johnny Smith", "J. Smith"],
        "is_dead": false,
        "current_addresses": [
          { "id": "A9876543210", "address": "123 Main St, New York, NY 10001" }
        ],
        "historic_addresses": [
          { "id": "A1234567890", "address": "456 Oak Ave, Brooklyn, NY 11201" }
        ],
        "owned_properties": [
          { "id": "R5432109876", "address": "123 Main St, New York, NY 10001" }
        ],
        "phones": [{ "number": "(212) 555-0198", "type": "mobile", "score": 92 }],
        "emails": ["john.smith@example.com"],
        "date_of_birth": "1985-03-15",
        "linkedin_url": "https://linkedin.com/in/johnsmith",
        "company_name": "Acme Corp",
        "job_title": "Software Engineer",
        "relatives": [{ "id": "P0987654321", "name": "Jane Smith" }]
      }
    ]
    ```

    Each record includes identifiers, addresses, phone numbers, emails, employment information, and linked property and relative records when available.
  </Step>
</Steps>

<Callout type="info" title="Understanding Phone Scores">
  Each phone number includes a **score** indicating **relative confidence** in
  the record's accuracy. A Higher score means that a number is more likely to be
  accurate than a lower score.
</Callout>

## Request Parameters

Combine any of these parameters to refine your search:

| Parameter                      | Description                                               | Example       |
| ------------------------------ | --------------------------------------------------------- | ------------- |
| `name`                         | Full or partial name                                      | `John Smith`  |
| `first_name`                   | First name                                                | `John`        |
| `middle_name`                  | Middle name                                               | `Robert`      |
| `last_name`                    | Last name                                                 | `Smith`       |
| `phone`                        | Phone number                                              | `2125550198`  |
| `street`                       | Street address                                            | `123 Main St` |
| `city`                         | City name                                                 | `New York`    |
| `state_code`                   | Two-letter state code                                     | `NY`          |
| `zipcode`                      | ZIP code                                                  | `10001`       |
| `min_age`                      | Minimum age filter (18-65)                                | `25`          |
| `max_age`                      | Maximum age filter (18-65)                                | `55`          |
| `include_historical_locations` | Include historical addresses in search (default: `false`) | `true`        |

<Callout type="warn" title="Query Parameter Behavior">
  The API uses **AND logic**, meaning all parameters must match. For example,
  `first_name=John` will return records named John.
  `first_name=John&last_name=Smith` will only return those same records that
  also have the last name Smith.
</Callout>

**Example with multiple parameters:**

```
https://api.whitepages.com/v1/person?name=John%20Smith&zipcode=10001
```

## Response Codes

| Status                  | Description                   | Billable |
| ----------------------- | ----------------------------- | -------- |
| `200 OK`                | Request successful            | Yes      |
| `400 Bad Request`       | Missing or invalid parameters | No       |
| `403 Forbidden`         | Invalid API key               | No       |
| `404 Not Found`         | No matching record (by id)    | Yes      |
| `429 Too Many Requests` | Rate limit exceeded           | No       |
| `5xx`                   | Server error                  | No       |

<Callout type="info">
  **Note**: A `200 OK` status means the request was processed successfully, but
  it doesn't guarantee results were found. Check the response body to see if any
  records were returned.
</Callout>

## Next Steps

Learn how to look up property ownership and resident data in the [Property Search](/documentation/property-search) tutorial.


# Search for Person by Partial Name



When you only have partial name information, use the individual name parameters (`first_name`, `middle_name`, `last_name`) to search more precisely than using the combined `name` parameter.

## When to Use Partial Name Search

Use individual name parameters when:

* You only know a person's first or last name
* You need to search across variations of a name
* You want more control over which parts of a name to match

## Search by Last Name Only

Find all people with a specific last name in a location:

```bash title="Request"
curl 'https://api.whitepages.com/v1/person?last_name=Smith&city=Seattle&state_code=WA' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

## Search by First and Last Name

When you know both first and last name but want to match regardless of middle name:

```bash title="Request"
curl 'https://api.whitepages.com/v1/person?first_name=John&last_name=Smith&state_code=NY' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

## Include Middle Name for Precision

For more precise matching when you have complete name information:

```bash title="Request"
curl 'https://api.whitepages.com/v1/person?first_name=John&middle_name=Robert&last_name=Smith&zipcode=10001' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

## Combining with Location Parameters

For best results, always include at least one location parameter:

| Combination                            | Use Case                    |
| -------------------------------------- | --------------------------- |
| `last_name` + `state_code`             | Broad search within a state |
| `last_name` + `city` + `state_code`    | City-level search           |
| `first_name` + `last_name` + `zipcode` | Precise local search        |

## Name Parameter vs Individual Parameters

| Parameter                  | Behavior                                               |
| -------------------------- | ------------------------------------------------------ |
| `name`                     | Matches against the full name field, flexible ordering |
| `first_name` + `last_name` | Matches each field specifically, more precise          |

Use `name` for convenience when you have a full name string. Use individual parameters when you need precise control or only have partial information.


# Search by Address



Use address parameters to find people associated with a specific location. By default, searches match only current addresses. Enable `include_historical_locations` to also search historical addresses.

## Basic Usage

Search for people at a specific address:

```bash title="Request"
curl 'https://api.whitepages.com/v1/person?street=123%20Main%20St&city=Seattle&state_code=WA' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

This returns people whose **current address** matches the search criteria.

## Include Historical Addresses

To search both current and historical addresses, set `include_historical_locations=true`:

```bash title="Request"
curl 'https://api.whitepages.com/v1/person?street=123%20Main%20St&city=Seattle&state_code=WA&include_historical_locations=true' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

This returns people who currently live at the address **or** have previously lived there.

## Parameters

| Parameter                      | Type    | Default | Description                            |
| ------------------------------ | ------- | ------- | -------------------------------------- |
| `street`                       | string  | —       | Street address                         |
| `city`                         | string  | —       | City name                              |
| `state_code`                   | string  | —       | Two-letter state code                  |
| `zipcode`                      | string  | —       | ZIP code                               |
| `include_historical_locations` | boolean | `false` | Include historical addresses in search |

## Examples

### Search by ZIP Code Only

Find people in a specific ZIP code:

```bash
curl 'https://api.whitepages.com/v1/person?zipcode=98101' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Search by City and State

Find people in a specific city:

```bash
curl 'https://api.whitepages.com/v1/person?city=Portland&state_code=OR' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Find Previous Residents

Find anyone who has ever lived at an address:

```bash
curl 'https://api.whitepages.com/v1/person?street=456%20Oak%20Ave&city=Denver&state_code=CO&zipcode=80202&include_historical_locations=true' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Combine with Name Search

Find a specific person at an address:

```bash
curl 'https://api.whitepages.com/v1/person?name=John%20Smith&street=789%20Pine%20St&city=Austin&state_code=TX&include_historical_locations=true' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<Callout type="info" title="Historical Address Coverage">
  Historical address data varies by record. Some individuals may have extensive
  address history while others may only have current address information
  available.
</Callout>

## Response

The response includes both current and historical addresses for each person found:

```json title="Response"
[
  {
    "id": "P1234567890",
    "name": "John Smith",
    "aliases": ["Johnny Smith"],
    "is_dead": false,
    "current_addresses": [
      { "id": "A9876543210", "address": "123 Main St, Seattle, WA 98101" }
    ],
    "historic_addresses": [
      { "id": "A1234567890", "address": "456 Oak Ave, Portland, OR 97201" },
      { "id": "A2345678901", "address": "789 Pine St, San Francisco, CA 94102" }
    ],
    "owned_properties": [
      { "id": "R5432109876", "address": "123 Main St, Seattle, WA 98101" }
    ],
    "phones": [{ "number": "(206) 555-0198", "type": "mobile", "score": 92 }],
    "emails": ["john.smith@example.com"],
    "date_of_birth": "1985-03-15",
    "linkedin_url": "https://linkedin.com/in/johnsmith",
    "company_name": "Acme Corp",
    "job_title": "Software Engineer",
    "relatives": [{ "id": "P0987654321", "name": "Jane Smith" }]
  }
]
```

<Callout type="info" title="Current vs Historical">
  When `include_historical_locations=true`, the search matches against both
  `current_addresses` and `historic_addresses`. The response always includes
  both fields regardless of the search setting.
</Callout>


# Search by Radius



Use the `radius` parameter to find people within a specific distance of a location. This enables proximity-based searches, such as finding all people within 10 miles of a given address or city.

## Basic Usage

Search for people within a radius of a location:

```bash title="Request"
curl 'https://api.whitepages.com/v1/person?city=Seattle&state_code=WA&radius=10' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

This returns people whose **current address** is within 10 miles of Seattle, WA.

## How It Works

When you provide a `radius` parameter along with location information, the API:

1. **Geocodes the location** - Converts your address, city, or ZIP code into geographic coordinates (latitude/longitude)
2. **Searches by distance** - Finds people whose addresses fall within the specified radius
3. **Returns results** - Ordered by relevance and distance

<Callout type="info" title="Geocoding">
  The API automatically geocodes your location. If geocoding fails (e.g.,
  invalid address), the search gracefully falls back to standard address
  matching without distance filtering.
</Callout>

## Parameters

| Parameter                      | Type    | Default | Description                                   |
| ------------------------------ | ------- | ------- | --------------------------------------------- |
| `radius`                       | number  | —       | Search radius in miles (maximum: 100)         |
| `street`                       | string  | —       | Street address for center point               |
| `city`                         | string  | —       | City name for center point                    |
| `state_code`                   | string  | —       | Two-letter state code for center point        |
| `zipcode`                      | string  | —       | ZIP code for center point                     |
| `include_historical_locations` | boolean | `false` | Include historical addresses in radius search |

<Callout type="warning" title="Radius Limit">
  The maximum allowed radius is **100 miles**. Requests with larger values will
  be rejected.
</Callout>

## Examples

### Search by City with Radius

Find people within 5 miles of downtown Portland:

```bash
curl 'https://api.whitepages.com/v1/person?city=Portland&state_code=OR&radius=5' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Search by ZIP Code with Radius

Find people within 1 miles of a specific ZIP code:

```bash
curl 'https://api.whitepages.com/v1/person?zipcode=98101&radius=1' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Search by Full Address with Radius

Find people within 0.1 miles of a specific street address:

```bash
curl 'https://api.whitepages.com/v1/person?street=123%20Main%20St&city=Seattle&state_code=WA&zipcode=98101&radius=0.1' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Include Historical Addresses

Find people who currently live or have previously lived within 10 miles of a location:

```bash
curl 'https://api.whitepages.com/v1/person?city=Austin&state_code=TX&radius=10&include_historical_locations=true' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Combine with Name Search

Find a specific person within a radius:

```bash
curl 'https://api.whitepages.com/v1/person?name=John%20Smith&city=Denver&state_code=CO&radius=25' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

## Location Specification

You can specify the center point for radius searches in several ways:

### Street Address (Most Precise)

Provide a full street address for the most accurate center point:

```bash
curl 'https://api.whitepages.com/v1/person?street=456%20Oak%20Ave&city=Boston&state_code=MA&radius=5' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### City and State

Use city and state for a broader center point (typically the city center):

```bash
curl 'https://api.whitepages.com/v1/person?city=San%20Francisco&state_code=CA&radius=20' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### ZIP Code

Use a ZIP code as the center point:

```bash
curl 'https://api.whitepages.com/v1/person?zipcode=10001&radius=3' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

<Callout type="info" title="Geocoding Accuracy">
  * **Street addresses** provide the most precise center point - **ZIP codes**
    use the geographic center of the ZIP code area - **City/State** combinations
    use the city center coordinates For best results, provide as much location
    detail as possible.
</Callout>

## Response

The response format is identical to standard person searches, including all address, phone, and demographic information:

```json title="Response"
[
  {
    "id": "P1234567890",
    "name": "John Smith",
    "aliases": ["Johnny Smith"],
    "is_dead": false,
    "current_addresses": [
      { "id": "A9876543210", "address": "789 Pine St, Seattle, WA 98102" }
    ],
    "historic_addresses": [
      { "id": "A1234567890", "address": "456 Oak Ave, Seattle, WA 98101" }
    ],
    "owned_properties": [
      { "id": "R5432109876", "address": "789 Pine St, Seattle, WA 98102" }
    ],
    "phones": [{ "number": "(206) 555-0198", "type": "mobile", "score": 92 }],
    "emails": ["john.smith@example.com"],
    "date_of_birth": "1985-03-15",
    "linkedin_url": "https://linkedin.com/in/johnsmith",
    "company_name": "Acme Corp",
    "job_title": "Software Engineer",
    "relatives": [{ "id": "P0987654321", "name": "Jane Smith" }]
  }
]
```

<Callout type="info" title="Distance Not Included">
  The response does not include the calculated distance from the center point.
  Results are ordered by relevance score, which factors in distance along with
  other matching criteria.
</Callout>

## Error Handling

### Graceful Degradation

If the location cannot be geocoded (e.g., invalid address or service unavailable), the API automatically falls back to standard address matching without distance filtering:

```bash
# If geocoding fails, this behaves like a standard city/state search
curl 'https://api.whitepages.com/v1/person?city=InvalidCity&state_code=XX&radius=10' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Radius Too Large

Requests with radius values exceeding 100 miles will return a validation error:

```json title="Error Response"
{
  "error": {
    "code": 400,
    "message": "Bad Request",
    "long_message": "Request validation failed. Validation failed for field 'query -> radius'. Please check the provided data.",
    "meta": null
  },
  "wp_trace_id": "10860e0010134c52833b9a3cdbdacfd3"
}
```

## Best Practices

### Choose Appropriate Radius

* **Urban areas**: Use smaller radii (2-10 miles) for more targeted results
* **Suburban areas**: Use medium radii (10-25 miles) to cover broader regions
* **Rural areas**: Use larger radii (25-100 miles) to account for lower population density

### Combine with Other Filters

Radius searches work well with other parameters:

```bash
# Find people aged 30-40 within 15 miles of a location
curl 'https://api.whitepages.com/v1/person?city=Chicago&state_code=IL&radius=15&min_age=30&max_age=40' \
  --header 'X-Api-Key: YOUR_API_KEY'
```

### Performance Considerations

* Larger radii return more results but will take longer to process
* Combining radius with name or other filters improves performance
* Consider whether you need to use radius or if other filters like city and state would be sufficient

<Callout type="tip" title="Optimization">
  For best performance, combine radius searches with additional filters like
  name, age range, or phone number to narrow down results.
</Callout>


# Retrieve usage data for a specific time range



{/* This file was generated by Fumadocs. Do not edit this file directly. Any changes should be made by running the generation command again. */}

<APIPage document={"https://api.whitepages.com/openapi.json"} operations={[{"path":"/v1/account/usage/","method":"get"}]} />


# Gets person details by id



{/* This file was generated by Fumadocs. Do not edit this file directly. Any changes should be made by running the generation command again. */}

<APIPage document={"https://api.whitepages.com/openapi.json"} operations={[{"path":"/v1/person/{id}","method":"get"}]} />


# Search for a person by name, phone number, and address



{/* This file was generated by Fumadocs. Do not edit this file directly. Any changes should be made by running the generation command again. */}

<APIPage document={"https://api.whitepages.com/openapi.json"} operations={[{"path":"/v1/person/","method":"get"}]} />


# Get property details by address



{/* This file was generated by Fumadocs. Do not edit this file directly. Any changes should be made by running the generation command again. */}

<APIPage document={"https://api.whitepages.com/openapi.json"} operations={[{"path":"/v1/property/","method":"get"}]} />


# Get property by ID



{/* This file was generated by Fumadocs. Do not edit this file directly. Any changes should be made by running the generation command again. */}

<APIPage document={"https://api.whitepages.com/openapi.json"} operations={[{"path":"/v2/property/{property_id}","method":"get"}]} />


# Search for property by address



{/* This file was generated by Fumadocs. Do not edit this file directly. Any changes should be made by running the generation command again. */}

<APIPage document={"https://api.whitepages.com/openapi.json"} operations={[{"path":"/v2/property/","method":"get"}]} />