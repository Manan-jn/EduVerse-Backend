const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios'); // Import Axios
const { WebhookClient } = require('dialogflow-fulfillment');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

app.post('/mathsbot', async (req, res) => {
    const agent = new WebhookClient({ request: req, response: res });

    async function wolframAlphaQuery(agent) {
        const query = agent.parameters['math_query'];

        try {
            const response = await axios.get('http://api.wolframalpha.com/v1/result', {
                params: {
                    appid: 'ENTER YOUR APP ID',
                    i: query
                }
            });

            agent.add(`The result for ${query} is: ${response.data}`);
        } catch (error) {
            console.error('Error querying Wolfram Alpha:', error);
            agent.add('Sorry, I couldn\'t process the math query at the moment.');
        }
    }

    let intentMap = new Map();
    intentMap.set('WolframAlphaQuery', wolframAlphaQuery);

    agent.handleRequest(intentMap);
    console.log('Intent:', agent.intent); // Log the intent name
    console.log('Parameters:', agent.parameters); // Log the parameters received
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});








