const express = require('express');
const bodyParser = require('body-parser');
const { WebhookClient } = require('dialogflow-fulfillment');
const NewsAPI = require('newsapi');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

const newsapi = new NewsAPI('ENTER YOUR API KEY');

app.post('/newsbot', (req, res) => {
    const agent = new WebhookClient({ request: req, response: res });

    async function getTopHeadlines() {
        try {
            const topHeadlinesResponse = await newsapi.v2.topHeadlines({
                language: 'en',
            });

            const headlines = topHeadlinesResponse.articles.map(article => article.title);
            agent.add(`Here are the top headlines: ${headlines.join(', ')}`);
        } catch (error) {
            console.error('Error fetching top headlines:', error);
            agent.add('Sorry, I couldn\'t fetch the top headlines at the moment.');
        }
    }

    async function getNewsByKeyword(agent) {
        const keyword = agent.parameters['keyword'];

        try {
            const newsByKeywordResponse = await newsapi.v2.everything({
                q: keyword,
                language: 'en',
            });

            const newsByKeyword = newsByKeywordResponse.articles.map(article => article.title);
            agent.add(`Here are the news articles related to ${keyword}: ${newsByKeyword.join(', ')}`);
        } catch (error) {
            console.error(`Error fetching news for keyword "${keyword}":`, error);
            agent.add(`Sorry, I couldn't fetch news for ${keyword} at the moment.`);
        }
    }

    let intentMap = new Map();
    intentMap.set('GetTopHeadlines', getTopHeadlines);
    intentMap.set('GetNewsByKeyword', getNewsByKeyword);

    agent.handleRequest(intentMap);
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
