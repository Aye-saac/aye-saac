## intent: read
- can you summarize [this](designator)
- what does [this](designator) say
- can you read [this](designator) for me
- can you let me know what [this](designator) says

## intent:allergen_info
- does [this](designator) contain [nuts](allergen)
- does [this](designator) contain any [nuts](allergen) in [it](designator)
- does [it](designator) contain [peanuts](allergen) 
- does [this](designator) have [sesame](allergen)
- does [it](designator) have [shellfish](allergen) in [it](designator)
- does [it](designator) include [gluten](allergen)
- has [that](designator) got [eggs](allergen) in [it](designator)
- is there any [milk](allergen) in [here](designator)
<<<<<<< Updated upstream
- does [this](designator) contain [gluten](allergen) 
- does this have [sesame](allegen) in [it](designator)

## intent:cooking_info
- how do [I](user) cook [this](designator)
- how do [I](user) prepare [this](designator)
- how [long](data) do [we](user) cook [this](designator) for
- can [it](designator) go in the [microwave](appliance)
- do [I](user) put [this](designator) in the [oven](appliance)
- do [you](user) have to take [this](designator) out of its packaging
- what [temperature](data) do [I](user) cook [it](designator) at
- what do [I](user) cook [this](designator) [with](appliance)

## intent:safety_info
- can [I](user) eat [this](designator)
- is [this](designator) [safe](safety) to eat
- will [we](user) [die](safety) if we eat [these](designator)
- can [I](user) [consume](safety) [this](designator)
- is [this](designator) [okay](safety) to eat

## intent:expiration_info
- is [this](designator) in [date](date)
- are [those](designator) out of [date](date)
- how long is [this](desingator) [good for](date)
- how many days are [these](designator) [good for](date)
- when does [it](designator) [expire](date)
- is [this](designator) still [good to eat](date)
- when do [these](designator) [go off](date)
=======
- can you check if [this](designator) food has [milk](allergen)
- are [eggs](allergen) one of the ingredients in [this](designator)
- I can't eat [fish](allergen), can I eat [this](designator)
- I cannot eat [celery](allergen), is [this](designator) safe for me
- I can't eat [dairy](allergen) products, so is [this](designator) okay for me to eat 
- I'm allergic to [soy](allergen), can I eat [this](designator)
- I'm [lactose](allergen) intolerant, will [this](designator) make me feel sick
- what [allergens](allergen) are in [this](designator) product
- does [this](designator) product contain traces of [nuts](allergen)

## intent:cooking_info
- how do [I](user) cook [this](designator)
- how long do [we](user) cook [this](designator) for
- what should [I](user) do to cook [this](designator)
- can [it](designator) go in the microwave
- can [I](user) cook this in the over
- how do [I](user) cook this
- how should [I](user) cook this
- do [I](user) put [this](designator) in the oven
- do [you](user) have to take [this](designator) out of its packaging
- what temperature do [I](user) cook [it](designator) at
- how long should [I](user) cook [this](designator) for, and at what temperature
- read me the instructions to make [this](designator)
- are there any instructions to prepare [this](designator)
- [I](user) want to cook [this](designator)
- help [me](user) make [this](designator)

## intent:expiration_info
- is [this](designator) in date
- are [those](designator) out of date
- how long is [this](desingator) good for
- how many days are [these](designator) good for
- when does [it](designator) expire
- is [this](designator) still good to eat
- when do [these](designator) go off
- when is the expiration date
- when is the use by date
>>>>>>> Stashed changes

## intent:safety_info
- can [I](user) eat [this](designator)
- is [this](designator) safe to eat
- will [we](user) die if we eat [these](designator)
- am [I](user) okay to eat this
- am [I](user) safe to eat this

## intent:nutritional_info
- how much [salt](nutri) is in [here](designator)
- how much [fat](nutri) does [this](designator) have in it
<<<<<<< Updated upstream
- how many [calories](nutri) does [this](designator) contain
=======
- how many [calories](nutri) are in [this](designator)
- is there a lot of [sugar](nutri) in [this](designator)
>>>>>>> Stashed changes
- is [this](designator) [alcohol](nutri) free
- is [this](designator) ok for [diabetics](user)
- is [this](designator) low [sodium](nutri)
- is [this](designator) suitable for [vegetarians](user)
- is [this](designator) ok for [vegans](user)
<<<<<<< Updated upstream
- what [vitamins](nutri) does [this](designator) have in it
- what type of [vitamins](nutri) are in [this](designator)
=======
- can you tell me about the [nutritional information](nutri) [this](designator) 
- tell me about the [nutritional information](nutri)
- what is the [nutritional information](nutri) of [this](designator) 

## intent:servings_info
- how many does [this](designator) serve
- does [this](designator) serve [three](desired_servings) people
- how much is left
- what's the number of servings
- how many servings are in [here](designator)
>>>>>>> Stashed changes

## intent:flavour_info
- is [this](designator) [spicy](flavour)
- how [hot](flavour) is [this](designator)
- how [strong](flavour) is [it](designator)
- what flavour are [these](designator)

## intent:storage
- how do [you](user) store [it](designator)
- can [I](user) freeze [this](designator)
- can [this](designator) be frozen
- does this need to be kept in the fridge

## intent:recycle_info
- is [this](designator) recyclable
- can I recycle [this](designator)

## intent: greet
- hello
- good morning
- hi

## intent: affirm
- let's do it
- i love that
- it's perfect
- that looks great
- yes
- yes of course

## intent: deny 
 - no thank you
- do you have something else
- no this does not work for me
- no i don't like that
- no
- no thanks

## intent: thanking
- you rock
- thanks
- thank you