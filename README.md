# Content Spread

Set of tools for reposting content between platforms. Built to speed up the sharing of content while following best practices for credit.

** Warning: this script is designed for personal usage. It doesn't have significant checks for edge cases, nor does it sanitise inputs **

## Setup

This project uses python. An `environment.yml` file is provided for replication via anaconda.

## File Descriptions
### Generate Post

Script to create formatted posts. Downloads images from a set of links, stores source links and short-form attributions, and a title for the post.

### Reddit Upload

Upload a post to reddit based on stored data. Formats the post including attribution and title, uploads to imgur hosting, and posts a comment with the full set of sources.