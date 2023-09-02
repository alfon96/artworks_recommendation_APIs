# Naples Artwork Recommender API

## Overview

This repository contains the source code for a FastAPI based API that provides personalized artwork recommendations in Naples based on a user's preferences. The API connects to a third-party database to fetch user information and preferences using their unique user ID. It employs a cosine similarity matrix algorithm to match users with artworks they are most likely to appreciate. Additionally, the API offers two recommendation types:

1. **raccomandazione_per_utente:** This focuses solely on matching artworks to a user's preferences.
2. **raccomandazione_per_contenuto:** This not only considers the user's preferences but also takes into account the metatag information of artworks, offering a more nuanced recommendation.

## Description

This repository contains the code for an API built using FastAPI in Python. This API provides recommendations for artworks located in Naples, based on user preferences stored in a third-party database. The API connects to this database to retrieve user preferences using their User ID. Recommendations are generated using a cosine similarity matrix algorithm.

## Features

- FastAPI based RESTful API
- Custom HTML/CSS landing page at the root URL featuring the company's logo
- Dockerized application for easy deployment and scalability
- JWT Authentication
- Additional batch script for automated multi-port testing
- Comprehensive tests for API functionality
- Data visualization using Matplotlib
- Connection to third-party database for user information retrieval

## Important Note

**Sensitive Data**: All sensitive data like API keys and passwords are not included in this repository. If you wish to try out this application, please visit [recommendationAPIs](http://ec2co-ecsel-1xcozup9p9r0a-1119021606.eu-central-1.elb.amazonaws.com/docs).

**Credentials**
- username: user
- password: ef03dc802d25031e

## Landing Page

When you navigate to the root URL of the API, you will be greeted with a custom HTML/CSS landing page that displays the logo of the company who commissioned this API.

## Automated Multi-Port Testing

This repository includes a batch script that automates the process of building and starting Docker images at different ports. This is particularly useful for brute-force testing to ensure that the API can handle all `user_id` values without crashing due to corner cases.

## Getting Started

### Requirements

- Python 3.9+
- Docker
- Third-party database credentials

### Installation

1. Clone the repository:
   git clone https://github.com/alfon96/naples_artworks_recommendation_APIs.git

2. Navigate to the directory:
   cd naples-artwork-recommender

3. Build the Docker image:
   docker build -t naples-artwork-recommender .

4. Run the container:
   docker run -p 8000:8000 naples-artwork-recommender

## Usage

You can interact with the API at `http://localhost:8000`. Please refer to the API documentation available at `http://localhost:8000/docs` for details on available endpoints and how to authenticate using JWT tokens.

## Testing

This repository contains extensive tests to ensure API functionality. Tests are run on N different local servers created through the Docker image, with a brute-force approach to test each user ID for corner cases and unhandled errors. To run the tests:
docker exec -it [CONTAINER_ID] pytest

yaml
Copy code

## Data Visualization

Matplotlib is used to visualize the results of the recommendations, which can provide useful insights into the effectiveness of the recommendation algorithm, the quality of artwork metatags, and the database goodness.

---

For more details, please contact me at my email address: alfalcone1996@gmail.com
