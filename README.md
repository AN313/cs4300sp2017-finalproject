# cs4300sp2017-finalproject

## Airbnb pricing suggestion

Airbnb is well-known for its renting and listing services. However, we have seen a lot of articles and blogs online asking about how to choose a right listing price. Airbnb's official website does not provide any specific instructions on how to pick a right price besides some general tips. Many travelers are also not sure if the listing price they are going to pay for their stay is too high.
The goal of our project is to build a query system that helps the hosts to decide how much they should charge for their new listing and helps users to decide if an existing listing price is reasonable. We take the input from users which includes the listing description and listing features and then use machine learning algorithm to predict possible price ranges. We plan to use existing online scripts to crawl data from Airbnb website. We will mainly use listing description, listing's features and listing price for our dataset. One of the possible machine learning algorithms would be Naive Bayes algorithm with multinomial feature vectors consisting of natural language sentimental analysis on the description and Airbnb listing features. Besides the suggesting price, we will also return a ranked list of similar listings (using some similarity measure on the feature vector) and how influential each feature is on the final suggested price.

Naxin Chen (nc352), Yiwei Ni (yn254), Ke Qian (kq32), Jim Yu (jly29)
