
# Understanding the Football Transfer Value Predictor

*A simpler explanation of the project for people who aren't familiar with machine learning.*

[← Back to Main README](README.md)

---

## What is This Project About?

If you follow football, you've probably seen discussions about how much certain players are worth.

For example, why is one striker worth €100 million while another is worth €20 million? What actually determines a player's market value?

I wanted to see whether machine learning could estimate these values using information such as a player's age, position, goals, assists, playing time, and other performance statistics.

Essentially, **I wanted to see how accurately a computer could estimate a football player's market value using statistics from one Premier League season.**

I used Transfermarkt's historical market valuations as the values my model was trying to predict.

One important thing to understand is that **market value is not the same as a transfer fee**. A player could be valued at €50 million, but a club might pay substantially more or less to sign them.

---

## How Does the Model Work?

Think of it this way.

Imagine you were given statistics for hundreds of football players, along with how much each player was worth.

You might start noticing patterns.

For example:
- Younger players with strong performances might have higher valuations.
- Players who regularly score goals might be valued differently from those who rarely score.
- Playing position might influence which statistics matter most.

A machine learning model tries to identify these relationships mathematically.

For this project, I collected player statistics and market valuations from three Premier League seasons:

- 2023–24
- 2024–25
- 2025–26

I used the first two seasons to train the model.

Then, I gave the model player statistics from 2025–26 and asked it to predict their market values after that season.

Finally, I compared those predictions with the actual Transfermarkt valuations.

**The important part is that the model wasn't given the 2025–26 market values when making its predictions.**

---

## How Accurate Was the Model?

My final Random Forest model achieved the following results for the 2025–26 season:

| Metric | Result |
| --- | --- |
| Mean Absolute Error (MAE) | €9.29 million |
| Root Mean Squared Error (RMSE) | €14.46 million |
| R² Score | 0.6102 |

These numbers might not mean much at first, so here's what they actually tell us.

### 1. Mean Absolute Error (MAE)

**€9.29 million**

This means that, across all 460 players evaluated, the model's predictions were approximately €9.29 million away from their actual market valuations on average.

However, this doesn't mean every prediction was off by exactly €9.29 million.

Some predictions were much closer, while others were off by tens of millions.

### 2. Root Mean Squared Error (RMSE)

**€14.46 million**

This measures prediction errors too, but it gives larger mistakes more weight.

For example, predicting a €100 million player to be worth only €40 million is a much larger mistake than predicting a €10 million player to be worth €8 million.

RMSE emphasizes mistakes like the first example more strongly.

Because our RMSE is noticeably higher than our MAE, we can see that some of the model's predictions had particularly large errors.

### 3. R² Score

**0.6102**

R² measures how well the model accounts for differences in player market valuations.

Our result of 0.6102 means that the model explains approximately 61% of the variation in the evaluated market values, relative to a baseline that always predicts the average value.

It doesn't mean that 61% of individual predictions were correct.

The model learned useful relationships, but there's still a significant amount of variation it couldn't explain.

---

## Where Did the Model Struggle?

One of the most interesting patterns was that **the model consistently underestimated expensive players**.

Here are a few examples from the 2025–26 evaluation:

| Player | Actual Market Value | Predicted Market Value |
| --- | ---: | ---: |
| Erling Haaland | €200M | €120.9M |
| Florian Wirtz | €100M | €45.2M |
| Cole Palmer | €100M | €36.9M |
| Estêvão | €80M | €18.4M |
| Moisés Caicedo | €100M | €40.7M |

The problem becomes clearer when we group players by their actual market valuations.

| Player Market Value | Average Prediction Error (Absolute) |
| --- | ---: |
| Under €10M | €4.69M |
| €10M–30M | €5.79M |
| €30M–60M | €13.40M |
| Over €60M | €33.81M |

The more expensive the players were, the larger our average prediction errors tended to become.

In fact, **all 40 players valued above €60 million were underestimated** by the model.

This was one of the biggest findings of the project.

---

## Why Was the Model So Far Off?

At first, I thought these results just meant my model wasn't very accurate.

But after looking at the specific players it struggled with, I started noticing some reasonable football-related explanations.

### Previous Performances Still Matter

Take Florian Wirtz, for example.

Wirtz established much of his reputation and high market valuation through his performances at Bayer Leverkusen in the Bundesliga.

When he moved to Liverpool, his Premier League performances didn't immediately match the expectations created by his previous success.

However, my model only had access to his Premier League statistics for the season.

**It didn't know what Wirtz had accomplished in Germany.**

This creates a problem because the football market evaluates a player's broader career, while my model mainly evaluates their performance in a single Premier League season.

### Injuries Can Affect Statistics Without Eliminating a Player's Value

Another issue is injuries.

Players such as Bukayo Saka and Estêvão experienced injury-related disruptions that affected their ability to contribute consistently.

A player who misses matches might have fewer goals, assists, or total minutes.

But this doesn't necessarily mean their underlying ability has disappeared or that their market valuation will immediately decline by the same amount.

The model doesn't have a full understanding of these circumstances.

It sees the statistics, but not necessarily the reasons behind them.

### Market Value Isn't Based on Statistics Alone

Football valuations can also depend on:

- A player's reputation and established ability.
- Their age and future potential.
- Previous performances in other leagues.
- Injury history and availability.
- Remaining contract length.
- Club circumstances and transfer-market demand.

These factors help explain why a player's estimated market value isn't always consistent with their statistics from one season.

These are possible explanations for the errors, rather than causes I have definitively proven through the model.

---

## Explore the Predictions Yourself

I created an interactive scatterplot that compares each player's actual market valuation against the model's prediction.

**[Open the Interactive Scatterplot](https://nothd7561.github.io/footy-transfer-value-predictor/)**

Each point represents a player.

- The horizontal axis shows the player's actual market value.
- The vertical axis shows the model's predicted value.
- The diagonal line represents a perfect prediction.
- Points below the line represent underestimates.
- Points above the line represent overestimates.

You can hover over individual points to see the player's name, position, actual value, predicted value, and prediction error.

The 10 most valuable players are highlighted to make them easier to identify.

---

## Was the Project Successful?

I think it was.

The point of this project wasn't to create a perfect system for predicting football player valuations.

I wanted to apply what I've learned about programming, data processing, and machine learning to something I genuinely enjoy.

I built a pipeline that collected football statistics, connected those statistics to historical market valuations, trained different regression models, and evaluated the results.

I also learned that getting a reasonable prediction isn't the same thing as understanding everything that influences the result.

**One of my biggest takeaways was that understanding why a machine learning model makes mistakes can be just as important as trying to improve its accuracy.**

There are definitely improvements I could make in the future, including incorporating performance from other leagues or training separate models for different positions.

For now, I'm treating this as the completed first version of the project.

---

[← Back to Main README](README.md)

[↑ Back to Top](#understanding-the-football-transfer-value-predictor)
