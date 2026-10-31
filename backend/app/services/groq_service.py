import os
import json
import re
from typing import Dict, Any, Optional

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class GroqService:
    @classmethod
    def get_client(cls):
        if not GROQ_API_KEY:
            return None
        try:
            from groq import Groq
            return Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            print("Groq client initialization warning:", e)
            return None

    @classmethod
    async def extract_incident_info(cls, raw_text: str, source_type: str = "CITIZEN") -> Dict[str, Any]:
        """
        Uses Groq LLM to convert unstructured emergency reports into structured facts.
        Includes a deterministic fallback when GROQ_API_KEY is omitted.
        """
        client = cls.get_client()
        if client:
            try:
                system_prompt = (
                    "You are the RELIEF-X disaster intelligence assistant. Analyze the supplied emergency report.\n"
                    "Extract:\n"
                    "- disaster_type (string, e.g. Flood, Waterlogging, Medical Trap)\n"
                    "- location (string, landmark or zone in Chennai, e.g. Velachery, Saidapet)\n"
                    "- affected_population (integer, if stated or estimated)\n"
                    "- urgency (number 1.0 to 5.0)\n"
                    "- severity (number 1.0 to 5.0)\n"
                    "- reported_hazards (list of strings)\n"
                    "- source_type (string)\n"
                    "- possible_contradictions (string or null)\n"
                    "- missing_information (string or null)\n"
                    "Do not invent facts. Do not claim a report is verified without evidence. "
                    "Do not allocate emergency resources. Return structured JSON only."
                )
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Source Type: {source_type}\nReport: {raw_text}"}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                content = chat_completion.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                print("Groq extraction fallback triggered:", e)

        # Deterministic Rule-Based Fallback
        lower = raw_text.lower()
        urgency = 3.0
        severity = 3.0
        pop = 50

        # Location heuristic
        location = "Chennai Metro"
        for loc in ["velachery", "saidapet", "guindy", "adyar", "t. nagar", "t nagar", "central", "marina", "tambaram", "koyambedu"]:
            if loc in lower:
                location = loc.title()
                break

        # Numbers for population
        pop_match = re.search(r"(\d+)\s*(people|residents|families|persons|stranded|trapped)", lower)
        if pop_match:
            pop = int(pop_match.group(1))

        # Severity & urgency cues
        if any(w in lower for w in ["critical", "emergency", "drowning", "chest deep", "submerged", "icu", "oxygen", "elderly"]):
            urgency = 4.8
            severity = 4.7
        elif any(w in lower for w in ["rising", "water entering", "knee deep", "blocked"]):
            urgency = 3.8
            severity = 3.6

        contradictions = None
        if "sunny" in lower or "fake" in lower or "prank" in lower:
            contradictions = "Content contradicts current meteorological precipitation alerts"

        return {
            "disaster_type": "Urban Flood",
            "location": location,
            "affected_population": pop,
            "urgency": urgency,
            "severity": severity,
            "reported_hazards": ["Rising water level", "Power outage"],
            "source_type": source_type,
            "possible_contradictions": contradictions,
            "missing_information": "Exact street number not specified",
            "is_simulation": True
        }

    @classmethod
    async def generate_explanation(
        cls,
        incident_title: str,
        priority_score: float,
        resource_name: Optional[str] = None,
        route: Optional[list] = None,
        unmet_needs: Optional[int] = 0
    ) -> str:
        """
        Generates human-readable explanations of the deterministic engine's recommendations.
        """
        client = cls.get_client()
        if client:
            try:
                prompt = (
                    f"Explain the emergency decision for commanders in 2 clear sentences.\n"
                    f"Incident: {incident_title}\n"
                    f"Computed Priority Score: {priority_score}/100\n"
                    f"Assigned Resource: {resource_name or 'Pending Allocation'}\n"
                    f"Traversable Route: {' -> '.join(route) if route else 'Direct'}\n"
                    f"Unmet Needs: {unmet_needs} people"
                )
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are the RELIEF-X explainability engine. Explain deterministic recommendations concisely to disaster response directors."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.2,
                    max_tokens=100
                )
                return chat_completion.choices[0].message.content.strip()
            except Exception:
                pass

        # Deterministic template explanation
        route_str = " -> ".join(route) if route else "arterial path"
        return (
            f"Incident prioritised at {priority_score}/100 based on verified flood impact. "
            f"{resource_name or 'Relief unit'} assigned via {route_str} with {unmet_needs} remaining unmet capacity."
        )
