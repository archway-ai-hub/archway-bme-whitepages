# Whitepages API Documentation

> Documentation for the Whitepages API

- [Documentation](/): Whitepages API Documentation
- [Getting Started](/documentation/getting-started): Get started with the Whitepages API
- [Getting a Trial API Key](/documentation/getting-trial-api-key): Step-by-step guide to signing up for a free Whitepages API trial
- [Guides](/documentation/guides): In-depth guides for using the Whitepages API
- [Property Search](/documentation/property-search): Get ownership and resident data for any property
- [Purchasing the API](/documentation/purchasing-api): Step-by-step guide to purchasing a Whitepages Pro API subscription
- [Authentication](/references/authentication): Learn how to authenticate your requests to the Whitepages API.
- [Billing](/references/billing): Understand how API usage is tracked and billed.
- [Routes](/references): Complete overview of all available Whitepages API endpoints organized by category.
- [Python SDK](/references/python-sdk): Official Python SDK for the Whitepages API.
- [Rate Limits](/references/rate-limits): Understand the rate limiting policies for the Whitepages API.
- [TypeScript SDK](/references/typescript-sdk): Official TypeScript SDK for the Whitepages API.
- [Filter by Age Range](/documentation/person-search/filter-by-age-range): Narrow person search results using minimum and maximum age filters
- [Person Search](/documentation/person-search): Look up individuals by name, phone, or address
- [Search for Person by Partial Name](/documentation/person-search/partial-name-search): Search for people using partial or incomplete name information
- [Search by Address](/documentation/person-search/search-by-address): Find people by current or historical addresses
- [Search by Radius](/documentation/person-search/search-by-radius): Find people within a specified distance of a location
- [Retrieve usage data for a specific time range](/references/account/get_account_usage_data): Retrieve API usage data for a specified date range.

Returns daily usage statistics including request counts for each day
within the specified time period. The response includes both individual
daily usage data and total usage for the entire period.

- The request count is total number of requests made including 2xx, 4xx
and 5xx responses. It is not the same as billable requests which is not
available right now as part of API.
- Maximum date range allowed: 90 days
- Dates are in UTC format
- Current day data when requested will be updated during the day
- Usage data is updated approximately every 30 minutes
- Usage data is returned only from the first date of actual usage in
the specified duration
- [Gets person details by id](/references/person/get_person_by_id): Retrieve detailed person information by Whitepages person ID.

This endpoint accepts a valid Whitepages person ID in the path parameter
and returns the complete person record if the ID exists in our data.
- [Search for a person by name, phone number, and address](/references/person/search_person_by_name_phone_or_address): Retrieve person information based on the provided query parameters.

This endpoint accepts a person query request and returns full details for
up to the top 15 matching persons from Whitepages data.
- [Get property details by address](/references/property/get_property_by_address): Retrieve property information based on the provided query parameters.

This endpoint accepts a property query request and returns the matching
property details if found within Whitepages data.
- [Get property by ID](/references/property-v2/get_property_by_id_v2): Retrieve property information by property ID.
- [Search for property by address](/references/property-v2/search_property_v2): Search for property by address parameters.

## Full Documentation

- [/llms-full.txt](/llms-full.txt): Complete documentation content