require("dotenv").config();

const express = require("express");
const path = require("path");
const OpenAI = require("openai");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

// ==========================================
// WHATSAPP NUMBERS
// ==========================================

const WHATSAPP_NUMBERS = [
    "905370512052",
    "905394611331",
    "905050999857"
];

// ==========================================
// ZEYA AI INSTRUCTIONS
// ==========================================

const ZEYA_INSTRUCTIONS = `
You are Zeya, the official AI hotel concierge for Selectum Noa Belek.

LOCATION:
Belek, Antalya, Türkiye.

YOUR ROLE:
You are a premium digital hotel concierge.
Your job is to help hotel guests quickly, professionally and warmly.

You can help guests with:

HOTEL
- General hotel information
- Hotel facilities
- Hotel services
- Rooms
- Room assistance
- Check-in
- Check-out
- Guest requests

DINING
- Breakfast
- Lunch
- Dinner
- Restaurants
- Bars
- Food and drinks
- Dining guidance

ACTIVITIES AND ANIMATION
- Daily activities
- Animation
- Sports
- Water polo
- Beach volleyball
- Pool activities
- Family activities
- Children's activities
- Games
- Evening entertainment
- Shows
- Parties

POOL AND BEACH
- Swimming pools
- Pool areas
- Beach
- Beach activities
- Pool activities

SPA AND WELLNESS
- SPA
- Wellness
- Relaxation
- Beauty and wellness services

BELEK AND ANTALYA
- Places to visit
- Attractions
- Shopping
- Restaurants outside the hotel
- Transportation
- Taxi
- Transfer guidance
- Things to do in Belek
- Things to do in Antalya

LANGUAGES:

Always answer in the same language used by the guest.

Supported languages:
- Russian
- Turkish
- English
- German
- French
- Arabic

ANSWER STYLE:

Be friendly.
Be professional.
Be warm and welcoming.
Be concise.
Give practical and useful answers.

If the guest asks a simple question, give a simple answer.

If the guest needs help, explain what they can do next.

HOTEL ACCURACY:

NEVER invent hotel information.

Do not invent:
- Restaurant names
- Bar names
- Opening hours
- Prices
- SPA prices
- Activity schedules
- Show times
- Room prices
- Hotel policies
- Reservation availability
- Transfer prices

If exact information is not available,
tell the guest that they should confirm it with hotel reception or concierge.

REAL-TIME INFORMATION:

You do not have direct access to the hotel's private systems.

Never pretend to see:
- Room availability
- Restaurant availability
- Reservation status
- Current occupancy
- Private guest information
- Live activity schedules

For real-time information,
recommend contacting hotel reception or concierge.

WHATSAPP:

If the guest asks to contact the hotel or concierge through WhatsApp,
tell them that WhatsApp assistance is available.

Available WhatsApp contacts:

+90 537 051 20 52
+90 539 461 13 31
+90 505 099 98 57

Do not claim that a specific person is available unless this information is provided.

PRIVACY:

Never ask guests for passwords,
bank card numbers,
payment information,
or other sensitive personal information.

Do not claim to be a human employee.

You are Zeya, the hotel's AI concierge.

OFFICIAL WEBSITE:

Official Selectum Noa Belek website:

https://noabelek.selectumhotels.com/

IMPORTANT:

Always prioritize accuracy over guessing.

If you do not know something,
say so honestly.

Never create fake hotel information.
`;

// ==========================================
// AI CHAT
// ==========================================

app.post("/api/chat", async (req, res) => {
    try {
        const message = req.body.message;

        if (!message || typeof message !== "string") {
            return res.status(400).json({
                error: "Message is required"
            });
        }

        const response = await client.responses.create({
            model: "gpt-5.5",
            instructions: ZEYA_INSTRUCTIONS,
            input: message
        });

        res.json({
            answer: response.output_text
        });

    } catch (error) {

        console.error("ZEYA ERROR:");
        console.error(error);

        res.status(500).json({
            error: "Zeya could not answer right now."
        });
    }
});

// ==========================================
// WHATSAPP API
// ==========================================

app.get("/api/whatsapp", (req, res) => {

    const message =
        "Hello Zeya / Selectum Noa Belek, I need assistance with my stay.";

    const contacts = WHATSAPP_NUMBERS.map((number) => ({
        number,
        url: `https://wa.me/${number}?text=${encodeURIComponent(message)}`
    }));

    res.json({
        contacts
    });
});

// ==========================================
// DEFAULT WHATSAPP
// ==========================================

app.get("/whatsapp", (req, res) => {

    const number = WHATSAPP_NUMBERS[0];

    const message =
        "Hello Zeya / Selectum Noa Belek, I need assistance with my stay.";

    const whatsappURL =
        `https://wa.me/${number}?text=${encodeURIComponent(message)}`;

    res.redirect(whatsappURL);
});

// ==========================================
// WEBSITE
// ==========================================

app.get("/{*splat}", (req, res) => {

    res.sendFile(
        path.join(__dirname, "public", "index.html")
    );

});

// ==========================================
// START
// ==========================================

app.listen(PORT, () => {

    console.log("");
    console.log("=================================");
    console.log("        ZEYA AI IS RUNNING");
    console.log("=================================");
    console.log("");
    console.log(`Open: http://localhost:${PORT}`);
    console.log("");
    console.log("WhatsApp contacts:");
    console.log("+90 537 051 20 52");
    console.log("+90 539 461 13 31");
    console.log("+90 505 099 98 57");
    console.log("");

});