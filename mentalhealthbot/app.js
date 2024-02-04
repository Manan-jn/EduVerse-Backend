const express = require("express");
const axios = require("axios");
const { WebhookClient } = require("dialogflow-fulfillment");
const app = express();
const cors = require("cors");

const key = "ENTER YOUR API KEY";
app.use(cors());
// Array to store the conversation
let conversation = [];
let mentalHealthSummary = "";

app.post("/webhook", express.json(), (req, res) => {
  const agent = new WebhookClient({ request: req, response: res });
  let intentMap = new Map();
  intentMap.set("Default Welcome Intent", welcome);
  intentMap.set("Default Fallback Intent", queryGPT);
  agent.handleRequest(intentMap);

  function welcome(agent) {
    agent.add(
      "Hi, I am your virtual personal mental health assistant. How are you doing today?"
    );
  }

  async function queryGPT(agent) {
    const OPENAI_API_KEY = key;

    const instance = axios.create({
      baseURL: "https://api.openai.com/v1/",
      headers: { Authorization: `Bearer ${OPENAI_API_KEY}` },
    });

    const dialog = [
      `The following is a conversation with an AI assistant that can have meaningful conversations with users. The assistant is helpful, empathic, and friendly. Its objective is to make the user feel better by feeling heard. With each response, the AI assistant prompts the user to continue the conversation in a natural way.`,
    ];

    let query = agent.query;
    console.log("querytext ", query);
    dialog.push(`User: ${query}`);
    dialog.push("AI:");

    const completionParams = {
      model: "gpt-3.5-turbo",
      messages: dialog.map((message, index) => {
        return { role: index % 2 === 0 ? "system" : "user", content: message };
      }),
    };

    try {
      const result = await instance.post("/chat/completions", completionParams);
      const botResponse = result.data.choices[0].message.content.trim();
      agent.add(botResponse);

      // Add the message to the conversation array
      addToConversation(`User: ${query}`, `AI: ${botResponse}`);
      // const convojson = JSON.stringify(conversation)
      // mentalHealthGPT(convojson);
    } catch (err) {
      console.log(err);
      agent.add("Sorry. Something went wrong. Can you say that again?");
    }
  }

  // Function to add a message to the conversation array
  function addToConversation(userMessage, botMessage) {
    conversation.push(userMessage);
    conversation.push(botMessage);
  }
});

// Route to get the entire conversation
app.get("/conversation", (req, res) => {
  res.json({ conversation });
});

// Route to generate a mental health report
app.get("/mentalHealthReport", async (req, res) => {
  try {
    // Extract user messages from the conversation
    const userMessages = conversation.filter(
      (message) => message.role === "user"
    );

    // Create a text string of user messages
    const userQuery = userMessages.map((message) => message.content).join(".");

    // // Extract the last three user messages or fewer
    // const userMessages = conversation
    //     .filter(message => message.role === 'user')
    //     .slice(-3);

    console.log("userMessages:", userMessages);

    // // Create a text string of user messages
    // const userQuery = userMessages.map(message => message.content).join(' ');
    console.log(conversation);
    console.log("userQuery:", userQuery);

    // Check if there are no user messages
    // if (!userQuery) {
    //     return res.json({ mentalHealthReport: "Your kid has not reported any mental health concerns" });
    // }

    // Use OpenAI API to generate a mental health report
    const OPENAI_API_KEY = key;
    const instance = axios.create({
      baseURL: "https://api.openai.com/v1/",
      headers: { Authorization: `Bearer ${OPENAI_API_KEY}` },
    });

    const dialog = [
      `For the ${conversation} take the last 2-3 sentences, and generate a mental health report for the parent of the user whose report has been generated. Also, suggest tips for the parent to help the user, i.e., the kid, to deal with the situation. Write the entire thing in a paragraph, straightforward and to the point.`,
    ];

    const completionParams = {
      model: "gpt-3.5-turbo",
      messages: dialog.map((message, index) => {
        return { role: "system", content: message };
      }),
    };

    const result = await instance.post("/chat/completions", completionParams);
    const mentalHealthReport = result.data.choices[0].message.content.trim();

    // Send the generated mental health report as JSON response
    res.json({ mentalHealthReport });
  } catch (err) {
    console.log(err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

// const dialog = [
//     `For the ${conversation} array, generate a mental health report for the parent of the user whose report has been generated. Also, suggest tips for the parent to help the user, i.e., the kid, to deal with the situation. Write the entire thing in a paragraph, straightforward and to the point.`,
// ];

const port = 3000;
app.listen(port, () => console.log(`App listening on port ${port}!`));
// const express = require("express");
// const axios = require('axios');
// const cors = require('cors');
// const { WebhookClient } = require("dialogflow-fulfillment");
// const app = express();

// app.use(cors());
// // Map to store conversations based on child IDs
// const conversationsByChildId = new Map();

// app.post("/webhook", express.json(), (req, res) => {
//     const agent = new WebhookClient({ request: req, response: res });
//     let intentMap = new Map();
//     intentMap.set("Default Welcome Intent", welcome);
//     intentMap.set("Default Fallback Intent", queryGPT);
//     agent.handleRequest(intentMap);

//     function welcome(agent) {
//         agent.add('Hi, I am your virtual personal mental health assistant. How are you doing today?');
//     }

//     async function queryGPT(agent) {
//         const OPENAI_API_KEY = key;

//         const instance = axios.create({
//             baseURL: 'https://api.openai.com/v1/',
//             headers: { Authorization: `Bearer ${OPENAI_API_KEY}` },
//         });

//         const dialog = [
//             `The following is a conversation with an AI assistant that can have meaningful conversations with users. The assistant is helpful, empathic, and friendly. Its objective is to make the user feel better by feeling heard. With each response, the AI assistant prompts the user to continue the conversation in a natural way.`,
//         ];

//         let query = agent.query;
//         console.log('querytext ', query)
//         dialog.push(`User: ${query}`);
//         dialog.push('AI:');

//         const completionParams = {
//             model: 'gpt-3.5-turbo',
//             messages: dialog.map((message, index) => {
//                 return { role: index % 2 === 0 ? 'system' : 'user', content: message };
//             }),
//         };

//         try {
//             const result = await instance.post('/chat/completions', completionParams);
//             const botResponse = result.data.choices[0].message.content.trim();
//             agent.add(botResponse);

//             // Add the message to the conversation array based on child ID
//             addToConversation(agent.originalRequest.payload.childId, `User: ${query}`, `AI: ${botResponse}`);

//         } catch (err) {
//             console.log(err);
//             agent.add('Sorry. Something went wrong. Can you say that again?');
//         }
//     }

//     // Function to add a message to the conversation array based on child ID
//     function addToConversation(childId, userMessage, botMessage) {
//         if (!conversationsByChildId.has(childId)) {
//             conversationsByChildId.set(childId, []);
//         }

//         conversationsByChildId.get(childId).push(userMessage);
//         conversationsByChildId.get(childId).push(botMessage);
//     }
// });

// // Route to get the conversation for a specific child ID
// app.get('/conversation', (req, res) => {
//     const childId = req.query.childId;
//     console.log('conversationsByChildId:', JSON.stringify([...conversationsByChildId]));

//     console.log('childId:', childId);
//     if (conversationsByChildId.has(childId)) {
//         res.json({ conversation: conversationsByChildId.get(childId) });
//     } else {
//         res.status(404).json({ error: 'Conversation not found for the specified child ID' });
//     }
// });

// const port = 3000;
// app.listen(port, () => console.log(`App listening on port ${port}!`));

// const express = require("express");
// const axios = require('axios');
// const { WebhookClient } = require("dialogflow-fulfillment");
// const app = express();
// const cors = require('cors');

// const key = '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';
// app.use(cors());
// // Array to store the conversation
// let conversation = [];

// app.post("/webhook", express.json(), (req, res) => {
//     const agent = new WebhookClient({ request: req, response: res });
//     let intentMap = new Map();
//     intentMap.set("Default Welcome Intent", welcome);
//     intentMap.set("Default Fallback Intent", queryGPT);
//     agent.handleRequest(intentMap);

//     function welcome(agent) {
//         agent.add('Hi, I am your virtual personal mental health assistant. How are you doing today?');
//     }

//     async function queryGPT(agent) {
//         const OPENAI_API_KEY = key;

//         const instance = axios.create({
//             baseURL: 'https://api.openai.com/v1/',
//             headers: { Authorization: `Bearer ${OPENAI_API_KEY}` },
//         });

//         const dialog = [
//             `The following is a conversation with an AI assistant that can have meaningful conversations with users. The assistant is helpful, empathic, and friendly. Its objective is to make the user feel better by feeling heard. With each response, the AI assistant prompts the user to continue the conversation in a natural way.`,
//         ];

//         let query = agent.query;
//         console.log('querytext ', query)
//         dialog.push(`User: ${query}`);
//         dialog.push('AI:');

//         const completionParams = {
//             model: 'gpt-3.5-turbo',
//             messages: dialog.map((message, index) => {
//                 return { role: index % 2 === 0 ? 'system' : 'user', content: message };
//             }),
//         };

//         try {
//             const result = await instance.post('/chat/completions', completionParams);
//             const botResponse = result.data.choices[0].message.content.trim();
//             agent.add(botResponse);

//             // Add the message to the conversation array
//             addToConversation(`User: ${query}`, `AI: ${botResponse}`);

//         } catch (err) {
//             console.log(err);
//             agent.add('Sorry. Something went wrong. Can you say that again?');
//         }
//     }

//     // Function to add a message to the conversation array
//     function addToConversation(userMessage, botMessage) {
//         conversation.push(userMessage);
//         conversation.push(botMessage);
//     }
// });

// // Route to get the entire conversation
// app.get('/conversation', (req, res) => {
//     res.json({ conversation });
// });

// const port = 3000;
// app.listen(port, () => console.log(`App listening on port ${port}!`));
