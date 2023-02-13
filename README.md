# ![](https://ga-dash.s3.amazonaws.com/production/assets/logo-9f88ae6c9c3871690e33280fcf557f33.png) Project 3: Web APIs & NLP

## Problem Statement

Everyone knows somebody who just can't help believing everything they read online, even if it's nonsense. Sometimes, what they're reading wasn't meant to be taken seriously at all, and was written as a joke. Identifying satire in the wild is a tough task, even for people.

Luckily, this is a task that natural language processing can handle. With the help of the PushShift API and webscraping, news articles on the border of fiction and reality can be gathered, analyzed, and labeled. The reddit communities, r/TheOnion and r/nottheonion, are dedicated to posting news articles. r/TheOnion links to articles written by The Onion, a well-known satire organization. r/nottheonion, on the other hand, links to real news that is so bizarre, you'll wish it was satirical. By aggregating news from these two sources, an NLP model stands a strong chance at being able to determine the boundary between satire and non-satire.

I will use NLP techniques on news articles sourced secondarily from Reddit to attempt to build a model which can successfully classify an article as satirical or real based only on its headline and body. Addtionally, I will attempt to answer whether satirical articles can be identified based only on their headlines, or if the body text is crucial to do so. If such a model is successful, it can be easily deployed in a number of ways, such as a browser extension, to help people everywhere maintain their sanity while scrolling through their news feed.

## Analysis

This analysis gathered over 500,000 posts from r/TheOnion and r/nottheonion. For each post, a web-scraping bot automatically retrieved the article body from the linked URL using Newspaper3k. This process failed large number of times and returned a null string, but in the end I was still left with 12,000 Onion articles, and 360,000 not-Onion articles. From this, I removed duplicates and then subsampled the not-Onion articles such that there was an equal number of both categories. This left me with just under 20,000 articles evenly split between both categories.

To each article, I removed stop words, punctuation, and whitespace, and then lemmatized the content. Additionally, I designed a scoring metric to determine if a word should be considered imbalnaced (appearing considerably more in one category than the other), and then automatically removed these words based on a threshold I determined.

These formatted articles were then fed into an instance of StackingClassifier, using a CountVectorizer and a RandomForest on the article bodies, and a TfidfVectorizer and RandomForest on the titles. These individual predictions were then fed into a LogisticRegression which made the final predictions. The individual models to use were determined by a grid search over a wide variety of models, including the two vectorizers, Naive Bayes, Logistic Regression, Random Forests and Extra Trees.

<p align="center">
  <img width="600" height="500" src="https://git.generalassemb.ly/alexwalshml/project_3/blob/main/assets/confusion.png">
</p>

The model achieved an accuracy of over 95%, and misclassification rates were balanced between the two categories. Visual inspection of two misclassified results revealed that both articles had several repeating words in the body, which may have been the source of error.

## Conclusions and Recommendations

There are two major ways to move forward with this project that I currently see. The first is to revisit the logarithmic imbalance score introduced in notebook 3. This scoring system proved to be very effective, as evidenced by the model's high accuracy. However, it is not perfect, and in hindsight could have been improved in its definition alone. The problem that I see with the function is that it weighs counts from both categories equally, even though one category contains far more text than the other. I would guess that using word frequencies instead of counts in each category would be a good place to start (and is equivalent in the case of balanced categories). Or, if that does not prove effective, the weights for each category can be treated as learnable parameters and chosen computationally. as it stands, equal weighting seems to be good enough, but I doubt it is optimal and should be explored further. On a similar note, very few threshold values were tested. Unit increases are quite large for a logarithmic scale, and it is possible that a lot of interesting information about a bias-variance tradeoff for the model is happening in between those integer values. The only reason I explored so few values was time constraints, and I believe a more fine-grained search would give even better results.

The second is to further analyze the cases of misclassification. If my hypothesis that wrongly labeled articles are caused by repeated terms is correct, then a more advanced vectorization technique may be required. Such a technique might implement diminishing returns for multiple instances of the same lemma within an article (such as the square root of count), so that classification is based more on the set of lemmas present as a whole, and less on how many of certain lemmas there are. This is little more than speculation, and requires in depth analysis of the articles the model mistook. Alternatively, the model could be suited with a reject option, and all of the "too close to call" articles could be fed to a secondary model specializing in hard-to-classify articles.

That said, over 95% accuracy is a potent model. Almost all of the classification power comes from from the article body and not the title, so it does not seem to be feasible to build a model based only on headlines. It may be possible with orders of magnitude more data, but as of now I recommend using both the title and article. I am happy with this model, and I'm fairly confident in its performance going forward as very little variance was observed during fitting. I propose two tests going forward. The first is to see how the model works on real, but non-bizarre news stories. The logic goes that if it can successfully differentiate satire and *almost*-satire, then boring old news should be easy enough to classify, yet this analysis did not test this. Second, see how well the model classifies other sources of satire. This model may prevent people from eating The Onion, but other publishers may have different styles the model is blind to.

Given passing results from those tests, I think the next steps are to prototype a model that accepts a URL and classifies it as real or satirical, and to deploy this model in beta as a browser extension. This would allow data to be gathered at a quick rate while leveraging user computation power, and would quickly lead to a better understanding of how the model works. This would give this model a better chance at success as a product.

