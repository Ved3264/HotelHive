from __future__ import annotations
from typing import Dict
from langchain.prompts import PromptTemplate


def build_base_system_prompt() -> PromptTemplate:
    """Generic assistant system prompt used across tools."""
    return PromptTemplate(
        input_variables=["data", "question"],
        template=(
            "You are HotelHive, a helpful hotel booking assistant.\n"
            "Use ONLY the provided hotel data to answer; do not fabricate details.\n\n"
            "Hotel data (records):\n{data}\n\n"
            "Guidelines:\n"
            "- Interpret the user's question and map terms to fields in the data.\n"
            "- Prefer concise, readable bullet lists for multi-item results.\n"
            "- If a requested field is not present, say it's not available.\n"
            "- If results are long, show first 50 and include 'showing 1–50 of N'.\n\n"
            "User question: {question}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"answer\": string,\n"
            "  \"items\": [\n"
            "    {\"hotel_id\": string, \"hotel_name\": string, \"city\": string, \"state\": string, \"room_type\": string, \"price\": number, \"amenities\": [string]}\n"
            "  ],\n"
            "  \"count\": number,\n"
            "  \"pagination\": {\"shown\": number, \"total\": number}\n"
            "}"
        ),
    )


def build_conversational_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["history", "input", "context", "available_tools"],
        template=(
            "You are HotelHive, a conversational hotel assistant.\n"
            "Be friendly, concise, and helpful. Use tools when they clearly help answer.\n\n"
            "Conversation so far (most recent last):\n{history}\n\n"
            "Context (data schema notes, constraints):\n{context}\n\n"
            "Available tools (name and brief purpose):\n{available_tools}\n\n"
            "User: {input}\n\n"
            "Decide the user's intent and whether to call a tool. If a tool is needed, select the single best\n"
            "tool and prepare minimal arguments. If no tool is needed, set tool to null and respond directly.\n\n"
        ),
    )


def build_search_hotels_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["data", "question"],
        template=(
            "You are a hotel search assistant.\n"
            "Use ONLY the provided hotel records.\n\n"
            "Data:\n{data}\n\n"
            "Instructions:\n"
            "- Support filtering by city, state, county, hotel_name, room_type, price, amenities.\n"
            "- Handle numeric ranges (e.g., 'under 150', 'between 100 and 200').\n"
            "- When listing, prefer concise structured output.\n\n"
            "Question: {question}\n\n"
        ),
    )


def build_check_availability_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["empty_rooms", "hotels", "hotel_id", "check_in", "check_out", "room_type"],
        template=(
            "You are an availability checker.\n"
            "Use ONLY the provided availability and hotel data.\n\n"
            "Availability data:\n{empty_rooms}\n\n"
            "Hotel catalog:\n{hotels}\n\n"
            "Task:\n"
            "- Determine if rooms are available for Hotel_ID={hotel_id} between {check_in} and {check_out}.\n"
            "- If room_type is provided ('{room_type}'), restrict results to that type.\n"
            "- Return a short list of matching rooms with dates and price.\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"hotel_id\": string,\n"
            "  \"check_in\": string,\n"
            "  \"check_out\": string,\n"
            "  \"available\": boolean,\n"
            "  \"count\": number,\n"
            "  \"rooms\": [\n"
            "    {\"room_type\": string, \"available_from\": string, \"available_to\": string, \"price\": number}\n"
            "  ]\n"
            "}"
        ),
    )


def build_create_booking_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=[
            "hotels",
            "hotel_id",
            "room_type",
            "guest_name",
            "contact_email",
            "check_in",
            "check_out",
            "guests_count",
        ],
        template=(
            "You are a booking assistant.\n"
            "Use ONLY the provided hotel data to validate inputs.\n\n"
            "Hotel catalog:\n{hotels}\n\n"
            "Create a booking summary for:\n"
            "- Hotel_ID: {hotel_id}\n- Room_Type: {room_type}\n- Guest: {guest_name}\n- Email: {contact_email}\n"
            "- Check-in: {check_in}\n- Check-out: {check_out}\n- Guests: {guests_count}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"booking_intent\": boolean,\n"
            "  \"reason\": string,\n"
            "  \"hotel_id\": string,\n"
            "  \"room_type\": string,\n"
            "  \"guest_name\": string,\n"
            "  \"contact_email\": string,\n"
            "  \"check_in\": string,\n"
            "  \"check_out\": string,\n"
            "  \"quote\": {\n"
            "    \"currency\": \"USD\",\n"
            "    \"nightly_price\": number,\n"
            "    \"nights\": number,\n"
            "    \"guests\": number,\n"
            "    \"total_price\": number\n"
            "  }\n"
            "}"
        ),
    )


def build_analytics_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["bookings", "hotels", "scope", "start_date", "end_date"],
        template=(
            "You are an analytics assistant for hotels.\n\n"
            "Hotel catalog:\n{hotels}\n\n"
            "Booking data:\n{bookings}\n\n"
            "Scope: {scope}\nPeriod: {start_date} to {end_date}\n\n"
            "Compute and report succinctly:\n"
            "- Total revenue and average booking value\n"
            "- Occupancy signals (proxy via booking counts)\n"
            "- Popular room types\n"
            "- Notable trends (up/down) in the selected period\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"period\": {\"start\": string, \"end\": string},\n"
            "  \"scope\": string,\n"
            "  \"metrics\": {\"total_revenue\": number, \"avg_booking_value\": number, \"total_bookings\": number},\n"
            "  \"popular_room_types\": [ {\"room_type\": string, \"bookings\": number} ],\n"
            "  \"notes\": [string]\n"
            "}"
        ),
    )


def build_dynamic_pricing_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["hotels", "bookings", "empty_rooms", "market_context", "target"],
        template=(
            "You are a dynamic pricing strategist.\n"
            "Use ONLY the provided data to recommend price adjustments.\n\n"
            "Hotel catalog:\n{hotels}\n\n"
            "Bookings (history):\n{bookings}\n\n"
            "Empty rooms (near-term inventory):\n{empty_rooms}\n\n"
            "Market context (seasonality, events, competitor hints):\n{market_context}\n\n"
            "Target objective: {target}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"recommendations\": [\n"
            "    {\n"
            "      \"hotel_id\": string, \n"
            "      \"room_type\": string, \n"
            "      \"current_price\": number, \n"
            "      \"suggested_price\": number, \n"
            "      \"expected_impact\": {\"occupancy\": \"up|down|neutral\", \"revenue\": \"up|down|neutral\"},\n"
            "      \"rationale\": string\n"
            "    }\n"
            "  ]\n"
            "}"
        ),
    )


def build_predictive_availability_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["bookings", "empty_rooms", "horizon_days", "filters"],
        template=(
            "You are forecasting availability.\n"
            "Using bookings history and current empty room spans, estimate availability over the next"
            " {horizon_days} days. Apply optional filters (city/state/hotel_id/room_type): {filters}.\n\n"
            "Bookings:\n{bookings}\n\nEmpty rooms:\n{empty_rooms}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"horizon_days\": number,\n"
            "  \"forecasts\": [ {\"hotel_id\": string, \"room_type\": string, \"date\": string, \"prob_available\": number} ],\n"
            "  \"highlights\": [string]\n"
            "}"
        ),
    )


def build_guest_matching_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["hotels", "guest_profile", "constraints"],
        template=(
            "You are a personalization engine.\n"
            "Match hotels to this guest profile using ONLY the provided hotel data.\n\n"
            "Guest profile:\n{guest_profile}\n\n"
            "Constraints (price caps, dates, location hints): {constraints}\n\n"
            "Hotel catalog:\n{hotels}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"matches\": [\n"
            "    {\n"
            "      \"hotel_id\": string, \"hotel_name\": string, \"score\": number, \n"
            "      \"price\": number, \"city\": string, \"state\": string, \n"
            "      \"amenities\": [string], \"rationale\": string\n"
            "    }\n"
            "  ]\n"
            "}"
        ),
    )


def build_multimodal_assistant_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are a multi-modal assistant.\n"
            "Given the context (which may reference voice/image/video metadata), answer the user's question clearly.\n\n"
            "Context:\n{context}\n\nQuestion: {question}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n  \"answer\": string, \n  \"references\": [string]\n}"
        ),
    )


def build_sentiment_analysis_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["feedback_corpus", "dimension"],
        template=(
            "Analyze sentiment of the following guest feedback.\n"
            "Dimension focus (optional): {dimension} (e.g., cleanliness, staff, amenities).\n\n"
            "Feedback:\n{feedback_corpus}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"overall_sentiment\": \"positive|neutral|negative\",\n"
            "  \"themes\": [ {\"theme\": string, \"sentiment\": \"positive|neutral|negative\"} ],\n"
            "  \"actions\": [string]\n"
            "}"
        ),
    )


def build_blockchain_verification_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["booking_record", "ledger_state"],
        template=(
            "You are verifying booking integrity using a hypothetical ledger.\n\n"
            "Booking record:\n{booking_record}\n\n"
            "Ledger snapshot:\n{ledger_state}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n  \"verified\": boolean, \n  \"reason\": string, \n  \"recommendation\": string\n}"
        ),
    )


def build_iot_integration_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["guest_preferences", "device_catalog"],
        template=(
            "You coordinate smart-room devices for a guest based on preferences.\n\n"
            "Guest preferences:\n{guest_preferences}\n\n"
            "Available devices:\n{device_catalog}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"plan\": [ {\"step\": number, \"action\": string} ],\n"
            "  \"defaults\": { \"temperature_c\": number, \"lighting\": string }\n"
            "}"
        ),
    )


def build_multilanguage_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["message", "target_language", "cultural_notes"],
        template=(
            "Translate and culturally adapt the message for the target audience.\n\n"
            "Message:\n{message}\n\nTarget language: {target_language}\nCultural notes: {cultural_notes}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n  \"translated\": string, \"language\": string, \"notes\": string\n}"
        ),
    )


def build_carbon_tracking_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["itinerary", "hotel_metadata"],
        template=(
            "Estimate the carbon footprint of this hotel stay itinerary using ONLY the provided metadata.\n\n"
            "Itinerary:\n{itinerary}\n\nHotel metadata (energy notes, green certifications, location):\n{hotel_metadata}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"rough_kg_co2e\": number,\n"
            "  \"drivers\": [string],\n"
            "  \"suggestions\": [string]\n"
            "}"
        ),
    )


def build_emergency_response_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["incident_report", "safety_playbook"],
        template=(
            "You are a safety coordinator.\n\n"
            "Incident report:\n{incident_report}\n\n"
            "Hotel safety playbook:\n{safety_playbook}\n\n"
            "Provide a minimal, ordered response checklist with immediate actions, contacts, and escalation rules.\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n"
            "  \"checklist\": [ {\"step\": number, \"action\": string} ],\n"
            "  \"contacts\": [string],\n"
            "  \"escalation\": string\n"
            "}"
        ),
    )


def build_ar_vr_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["hotel_media_index", "user_focus"],
        template=(
            "You curate an AR/VR tour plan given the user's focus (e.g., spa, ocean view, family rooms).\n\n"
            "Media index:\n{hotel_media_index}\n\n"
            "User focus: {user_focus}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n  \"scenes\": [ {\"order\": number, \"title\": string, \"caption\": string} ]\n}"
        ),
    )


def build_fraud_detection_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["booking_events"],
        template=(
            "You are screening booking events for fraud risk.\n\n"
            "Events:\n{booking_events}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n  \"risk_level\": \"low|medium|high\", \"signals\": [string], \"action\": string\n}"
        ),
    )


def build_loyalty_program_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["guest_history", "current_offers"],
        template=(
            "Design a personalized loyalty offer for the guest based on history and current offers.\n\n"
            "Guest history:\n{guest_history}\n\n"
            "Current offers:\n{current_offers}\n\n"
            "Return ONLY valid JSON with this structure:\n"
            "{\n  \"tier\": string, \"perks\": [string], \"pitch\": string\n}"
        ),
    )


def build_common_context(
    schema_hotels: list[str] | None = None,
    schema_empty_rooms: list[str] | None = None,
    schema_bookings: list[str] | None = None,
    capabilities: list[str] | None = None,
    policies: Dict[str, str] | None = None,
) -> str:
    """Build a reusable conversational context string.

    Provide lightweight schema, capabilities, and policy hints used by the
    conversational prompt. All parameters are optional; sensible defaults are used.
    """
    hotels_cols = schema_hotels or [
        "ID", "Hotel_ID", "Hotel_Name", "Details", "State", "County", "City",
        "Address", "Contact_Info", "Room_Type", "Price", "Amenities",
    ]
    empty_cols = schema_empty_rooms or [
        "EmptyRoom_ID", "Hotel_ID", "Hotel_Name", "Room_Type", "Available_From",
        "Available_To", "Price", "Status",
    ]
    booking_cols = schema_bookings or [
        "Booking_ID", "Hotel_ID", "Hotel_Name", "Room_Type", "Guest_Name",
        "Contact_Email", "Check_In_Date", "Check_Out_Date", "Guests_Count",
        "Total_Price", "Payment_Status",
    ]

    caps = capabilities or [
        "Hotel search (filters: city, state, room_type, price, amenities)",
        "Availability check (date ranges, room type)",
        "Booking summary & quote",
        "Analytics (revenue, occupancy proxy, room popularity)",
        "Advanced: dynamic pricing, predictive availability, personalization",
    ]

    pol = policies or {
        "json_only": "Responses must be valid JSON (no extra commentary).",
        "dates": "Use ISO-8601 YYYY-MM-DD for dates.",
        "currency": "Prices in USD (number).",
        "limits": "If results > 50, return first 50 and set pagination accordingly.",
        "safety": "If a field is missing, state not available; never invent data.",
    }

    lines: list[str] = []
    lines.append("Schemas:")
    lines.append(f"- hotels.xlsx columns: {', '.join(hotels_cols)}")
    lines.append(f"- empty_rooms_5000.xlsx columns: {', '.join(empty_cols)}")
    lines.append(f"- hotel_bookings.xlsx columns: {', '.join(booking_cols)}")
    lines.append("")
    lines.append("Capabilities:")
    for c in caps:
        lines.append(f"- {c}")
    lines.append("")
    lines.append("Policies:")
    for k, v in pol.items():
        lines.append(f"- {k}: {v}")

    return "\n".join(lines)


def get_prompt_registry() -> Dict[str, PromptTemplate]:
    """Return a mapping of feature name to a pre-built PromptTemplate.

    Note: Some prompts require runtime arguments and should be created via
    the corresponding build_* function if you need to vary input_variables.
    """
    return {
        # Core
        "base_system": build_base_system_prompt(),
        "conversational": build_conversational_prompt(),
        "search_hotels": build_search_hotels_prompt(),
        "check_availability": build_check_availability_prompt(),
        "create_booking": build_create_booking_prompt(),
        "analytics": build_analytics_prompt(),
        # Advanced
        "dynamic_pricing": build_dynamic_pricing_prompt(),
        "predictive_availability": build_predictive_availability_prompt(),
        "guest_matching": build_guest_matching_prompt(),
        "multimodal_assistant": build_multimodal_assistant_prompt(),
        "sentiment_analysis": build_sentiment_analysis_prompt(),
        "blockchain_verification": build_blockchain_verification_prompt(),
        "iot_integration": build_iot_integration_prompt(),
        "multilanguage": build_multilanguage_prompt(),
        "carbon_tracking": build_carbon_tracking_prompt(),
        "emergency_response": build_emergency_response_prompt(),
        "ar_vr": build_ar_vr_prompt(),
        "fraud_detection": build_fraud_detection_prompt(),
        "loyalty_program": build_loyalty_program_prompt(),
    }


__all__ = [
    
    "build_base_system_prompt",
    "build_conversational_prompt",
    "build_search_hotels_prompt",
    "build_check_availability_prompt",
    "build_create_booking_prompt",
    "build_analytics_prompt",
    "build_dynamic_pricing_prompt",
    "build_predictive_availability_prompt",
    "build_guest_matching_prompt",
    "build_multimodal_assistant_prompt",
    "build_sentiment_analysis_prompt",
    "build_blockchain_verification_prompt",
    "build_iot_integration_prompt",
    "build_multilanguage_prompt",
    "build_carbon_tracking_prompt",
    "build_emergency_response_prompt",
    "build_ar_vr_prompt",
    "build_fraud_detection_prompt",
    "build_loyalty_program_prompt",
    
    "get_prompt_registry",
    "build_common_context",
]


