const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 3000;

app.use(bodyParser.json());

app.post('/webhook', (req, res) => {
    const intent = req.body.queryResult.intent.displayName;

    if (intent === 'ReadAlong') {
        handleReadAlongIntent(req, res);
    } else {
        res.json({ fulfillmentText: 'I am not sure how to handle that.' });
    }
});

// function handleReadAlongIntent(req, res) {
//     const stories = [
//         { title: 'Level 1', url: 'https://readalong.google.com/book/sw_8040' },
//         { title: 'Level 2', url: 'https://readalong.google.com/book/sw_45764' },
//         { title: 'Level 3', url: 'https://readalong.google.com/book/sw_1042' },
//         { title: 'Level 4', url: 'https://readalong.google.com/book/KK_014' },
//     ];

//     const buttons = stories.map((story) => ({
//         text: story.title,
//         postback: story.url,
//     }));

//     res.json({
//         fulfillmentMessages: [
//             {
//                 card: {
//                     title: 'Choose a story to read along:',
//                     buttons,
//                 },
//             },
//         ],
//     });
// }

function handleReadAlongIntent(req, res) {
    const stories = [
        { title: 'Level 1', url: 'https://readalong.google.com/book/sw_8040' },
        { title: 'Level 2', url: 'https://readalong.google.com/book/sw_45764' },
        { title: 'Level 3', url: 'https://readalong.google.com/book/sw_1042' },
        { title: 'Level 4', url: 'https://readalong.google.com/book/KK_014' },
    ];

    const richContent = [
        [
            {
                "type": "info",
                "title": "Choose a story to read along:",
                "subtitle": "Click on the links below to start reading.",
                "image": {
                    "src": {
                        "rawUrl": "https://play-lh.googleusercontent.com/51WYc0ZPB34cGDB8MCkDc0ymv6iBf0r-kSZV_H5pXVDHvdVCA12TWUWQtS54zg-RodI=w240-h480-rw"
                    }
                }
            }
        ],
        [
            {
                "type": "chips",
                "options": stories.map(story => ({
                    "text": story.title,
                    "link": story.url
                }))
            }
        ]
    ];

    res.json({
       "fulfillment_messages":[
           {
               "payload": {
                   "richContent": richContent
               }
           }
       ]
    });
}


// function handleReadAlongIntent(req, res) {
//     const stories = [
//         { title: 'Level 1', url: 'https://readalong.google.com/book/sw_8040' },
//         { title: 'Level 2', url: 'https://readalong.google.com/book/sw_45764' },
//         { title: 'Level 3', url: 'https://readalong.google.com/book/sw_1042' },
//         { title: 'Level 4', url: 'https://readalong.google.com/book/KK_014' },
//     ];

//     const responseText = "Choose a story to read along:\n" +
//         stories.map(story => `${story.title}: ${story.url}`).join("\n");

//     res.json({
//         fulfillmentText: responseText,
//     });
// }


app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
