<!-- @format -->

# VIDY - A All in One Solution for Youtubers

Vidy is a flask application to analyze sentiment and summarize comments for a given YouTube video. This project helps you gain insights into the sentiments expressed in comments on YouTube videos and provides a summarized overview of the comments. It also provides a list of potential topic names that a YouTuber can consider to grow their channel.

## Key Features

-   Analyze sentiment of comments on a YouTube video.
-   Spam analysis of comments on a YouTube video.
-   Generate a summary of the comments on a YouTube video.
-   Generate a list of potential topic names that a YouTuber can consider to grow their channel.

## Table of Contents

-   [Prerequisites](#prerequisites)
-   [Getting Started](#getting-started)
-   [Usage](#usage)
-   [API Endpoints](#api-endpoints)
-   [License](#license)

## Prerequisites

Before getting started, make sure you have the following prerequisites installed and set up:

-   [Python 3.x](https://www.python.org/downloads/)
-   [YouTube API Key](https://developers.google.com/youtube/registering_an_application)
-   [OpenAI API Key](https://openai.com/)
-   [MindsDB Cloud Account](https://mindsdb.com/)

## Getting Started

### Installation

1. Clone this repository to your local machine:

    ```bash
    git clone https://github.com/AvaterClasher/vidy
    ```

2. Change into the project directory:

    ```bash
    cd vidy
    ```

3. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

4. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. Copy the .env.local file to a .env file and set the environment variables:

    ```bash
    cp .env.local .env
    rm .env.local
    ```

2. Make sure you have an internet connection to connect to the MindsDB Cloud server.

## Usage

1. Run the Flask application:

    ```bash
    python app.py
    ```

2. The application will start and be accessible at `http://localhost:5000`. You can make requests to the `/api/youtube` endpoint to analyze sentiment and get comment summaries for a specific YouTube video.

    Note : It may take some time to login to MindsDB Cloud and load the models.

## API Endpoints

- `GET /api/youtube`: Analyze sentiment and get comment summaries for a specific YouTube video.

  - Parameters:

    - `youtube_video_id`: The YouTube video ID for which you want to analyze comments.
    - `limit`: The maximum number of comments to analyze. Defaults to 10.
    - `sentiment`: Whether to generate a sentiment analysis of the comments. Defaults to `false`.
    - `spam`: Whether to generate a spam analysis of the comments. Defaults to `false`.
    - `comment_summary`: Whether to generate a summary of the comments. Defaults to `false`.
    - `recommendation`: Whether to generate a list of potential topic names that a YouTuber can consider to grow their channel. Defaults to `false`.

  - Example request:

    ```bash
    http://127.0.0.1:5000/api/youtube?youtube_video_id=uZdEsWOOhfA&limit=5&comment_summary=true&recommendation=true&sentiment=true&spam=true
    # The video id is the code after the website link -> https://www.youtube.com/watch?v=uZdEsWOOhfA here uZdEsWOOhfA is the video id.
    ```

  - Example response:

  ```json
  {
      "comment_summary": "In summary, the comments collectively praise Theo, likely an influential figure in open source development, for setting a new standard as a maintainer/wizard. There's appreciation for reaching out to the audience for ideas, with a specific emphasis on the positive practice of seeking assistance in web development. Additionally, there's acknowledgment of Theo's dedication to community contribution, even from someone who hasn't used the tool yet, noting a positive impact on their outlook on software development. Finally, a direct question is posed about configuring a library for a custom Minio bucket, expressing enthusiasm for potentially achieving \"infinite\" storage. Overall, the comments reflect a positive and appreciative sentiment towards Theo and their contributions to the open source community.",
      "recommendation": "Based on the comments, some potential topic names that a YouTuber can consider to grow their channel could be:\n\n1. Theo: A New Standard in Open Source Mastery\n2. The Power of Community Collaboration in Web Development\n3. Changing Perspectives: Theo's Impact on Software Development\n4. Dedication to Giving Back: Theo's Influence in Open Source\n5.Exploring Infinite Storage: Configuring Libraries with Minio Buckets",
      "sentiments": {
         "negative": 1,
         "neutral": 2,
         "positive": 2
      },
      "spams": 0
      }
  ```

  Note: Again, as models are rate limited, it may take some time to get the response (Approx: 2min/request).


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
