import fetch from "node-fetch";

const TOKEN = process.env.BOT_TOKEN;
const TELEGRAM_API = `https://api.telegram.org/bot${TOKEN}`;

export default async function handler(req, res) {
    if (req.method === "POST") {
        const body = req.body;

        if (body?.message) {
            const chatId = body.message.chat.id;
            const text = body.message.text || "";

            await fetch(`${TELEGRAM_API}/sendMessage`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    chat_id: chatId,
                    text: `Ти написав: ${text}`
                })
            });
        }

        res.status(200).send("OK");
    } else {
        res.status(200).send("This endpoint is for Telegram Webhook");
    }
}