## C

The chatbot is a **Retrieval-Augmented Generation (RAG)** system that allows users to ask natural language questions about disaster damage. It combines:

- **Retrieval** of pre‑computed damage assessment data (building-level classifications from aerial imagery analysis).
- **Generation** of fluent, context‑aware answers using a Large Language Model (LLM) like GPT.

The chatbot is integrated with the geospatial dashboard: answers can automatically pan/zoom the map and highlight relevant buildings.

## Planned User Flow

1. **User opens the dashboard** – The map shows an overview of the disaster area. The chat panel is visible on the side.

2. **User types a question** – For example: _“Show me destroyed buildings on Maple Street.”_

3. **Frontend sends a request** – The chat input triggers an HTTP POST to the backend endpoint `/api/chat` with a JSON body containing the query and an optional session ID.

4. **Backend processes the request** – This involves multiple sub-steps:
   - **Query Understanding**: Extracts key entities (location, damage level, **intent**).
   - **Retrieval**: Searches the damage database for matching records using spatial or keyword queries.
   - **Context Assembly**: Combines retrieved data, conversation history, and dashboard state into a structured prompt.
   - **LLM Call**: Sends the prompt to the LLM API and receives a generated answer.
   - **Response Formatting**: Packages the answer, relevant data, and map instructions into a JSON response.

5. **Frontend receives the response** – Updates the chat UI with the answer, and if `map_focus` is provided, instructs the map component to center/zoom and highlight buildings.

6. **User may ask a follow‑up** – The session ID allows the backend to remember previous context (e.g., the last mentioned street) for coherent multi‑turn conversations.

**Query Understanding** → **Retrieval** → **Context Assembly** (including history & dashboard state) → **LLM Generation** → **Response Formatting & Dashboard Updates**.

## Chatbot Input

```json
{
  "query": string,
  "session_id": string | number, // optional, for conversation continuity?
  "dashboard_context": {
  }, // optional, current map state
}
```

| Field               | Type              | Description                                                                                                      |
| ------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------- |
| `query`             | string            | The user's natural language question.                                                                            |
| `session_id`        | string (optional) | Unique identifier for the conversation session. If not provided, backend may generate one.                       |
| `dashboard_context` | object (optional) | Current map view and active filters, used to refine retrieval (e.g., only consider buildings currently visible). |

## Chatbot Output

```json
{
  "answer": "I found 3 destroyed buildings on Maple Street: 123 Maple (destroyed, 95% confidence), 456 Maple (destroyed, 92%), and 789 Maple (destroyed, 88%). I've centered the map on that area",
  "relevant_data": [
    {
      "id": "bldg001",
      "address": "123 Maple Street",
      "damage_level": "destroyed",
      "confidence": 0.95,
      "latitude": 40.7128,
      "longitude": -74.006,
      "pre_image": "url_to_pre_image",
      "post_image": "url_to_post_image"
    },
    {
      "id": "bldg002",
      "address": "456 Maple Street",
      "damage_level": "destroyed",
      "confidence": 0.92,
      "latitude": 40.713,
      "longitude": -74.0065,
      "pre_image": "...",
      "post_image": "..."
    }
  ],
  "map_focus": {
    "lat": 40.7129,
    "lng": -74.0062,
    "zoom": 17,
    "highlight_ids": ["bldg001", "bldg002", "bldg003"]
  },
  "suggested_followups": [
    "Show major damage on Maple Street",
    "What about Oak Street?",
    "Compare with Riverside"
  ],
  "session_id": "abc123xyz"
}
```

| Field                 | Type              | Description                                                                                                                      |
| --------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `answer`              | string            | The chatbot's natural language response.                                                                                         |
| `relevant_data`       | array (optional)  | List of damage records used to generate the answer. Can be displayed in a sidebar or as map markers.                             |
| `map_focus`           | object (optional) | Instructs the frontend to adjust the map. Contains center coordinates, zoom level, and optionally IDs of buildings to highlight. |
| `suggested_followups` | array (optional)  | Three to five example questions the user might ask next, displayed as clickable chips.                                           |
| `session_id`          | string            | Echoes the session ID (or newly generated) for subsequent requests.                                                              |

<!-- tell me the status of damage on Maple Street -->

```json
{
  "answer": "The building at 123 Maple Street in Downtown has been completely destroyed, with a confidence level of 0.95.",
  "relevant_data": [
    {
      "id": "bldg001",
      "address": "123 Maple Street",
      "neighborhood": "Downtown",
      "latitude": 40.7128,
      "longitude": -74.006,
      "damage_level": "destroyed",
      "confidence": 0.95,
      "pre_image": "url_to_pre_image",
      "post_image": "url_to_post_image"
    },
    {
      "id": "bldg004",
      "address": "101 Elm Street",
      "neighborhood": "Riverside",
      "latitude": 40.7135,
      "longitude": -74.008,
      "damage_level": "none",
      "confidence": 0.99,
      "pre_image": "...",
      "post_image": "..."
    }
  ],
  "map_focus": {
    "lat": 40.7128,
    "lng": -74.006,
    "zoom": 16
  },
  "suggested_followups": [
    "Show me destroyed buildings",
    "What's the damage in Riverside?",
    "Compare Downtown and Riverside"
  ]
}
```

<!-- did Maple Street take more damage than Elm Street? -->

```json
{
  "answer": "Yes, according to the data, Maple Street took more damage than Elm Street. The damage level at Maple Street is \"destroyed\" with a confidence of 0.95, while there was no damage reported at Elm Street (damage level = none) with a confidence of 0.99.",
  "relevant_data": [
    {
      "id": "bldg001",
      "address": "123 Maple Street",
      "neighborhood": "Downtown",
      "latitude": 40.7128,
      "longitude": -74.006,
      "damage_level": "destroyed",
      "confidence": 0.95,
      "pre_image": "url_to_pre_image",
      "post_image": "url_to_post_image"
    },
    {
      "id": "bldg004",
      "address": "101 Elm Street",
      "neighborhood": "Riverside",
      "latitude": 40.7135,
      "longitude": -74.008,
      "damage_level": "none",
      "confidence": 0.99,
      "pre_image": "...",
      "post_image": "..."
    }
  ],
  "map_focus": {
    "lat": 40.7128,
    "lng": -74.006,
    "zoom": 16
  },
  "suggested_followups": [
    "Show me destroyed buildings",
    "What's the damage in Riverside?",
    "Compare Downtown and Riverside"
  ]
}
```
