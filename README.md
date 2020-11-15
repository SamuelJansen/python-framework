# python_framework - v0.1.0-05 - FINALY OUT LOL
Basically, its a Flask wrapper

It alters Flask behaviours in order to make APIs better organized.

## Features
- NOT A SINGLE SERIALIZER IS NEEDED!
- OpenApiDocumentation 
- JwtSecutiry
- Suport for services, validators, helpers, converters, mappers, and repository
- SqlAlhemyProxy without the need to "open connection" due to circular import issues

### Requirements
- ```python_framework==0.1.0.post05```

### Package pattern
![Alt text](https://i.pinimg.com/originals/f6/b0/6a/f6b06aac4c675655a8ad8763f2afcbe4.jpg?raw=true "package_pattern")

### Globals.yml file
![Alt text](https://i.pinimg.com/originals/47/2f/d5/472fd582fac7483666e327e754be5df1.jpg?raw=true "globals_confituration_file")

### app.py and MyApi.py - just copy paste and be happy
![Alt text](https://i.pinimg.com/originals/e8/99/ff/e899ff77f1ecde64bf22175422691e63.jpg?raw=true "app_and_MyApi")

### Documentation example
https://feature-dataset-manager.herokuapp.com/swagger/ - it may take a while to load as heroku sometime sleeps...

### Controller examples
- Login controller
![Alt text](https://i.pinimg.com/originals/46/ad/f1/46adf1c4209bf789ae6cbc63828fd003.jpg?raw=true "login_controller")
- Feature controller
![Alt text](https://i.pinimg.com/originals/87/95/7d/87957d15526998de8ef4b587e8b89373.jpg?raw=true "feature_controller")

### Service examples
- User service
![Alt text](https://i.pinimg.com/originals/1b/77/54/1b7754ba9ba1067261aef67fead519bc.jpg?raw=true "user_service")
- Feature service
![Alt text](https://i.pinimg.com/originals/1b/77/54/1b7754ba9ba1067261aef67fead519bc.jpg?raw=true "feature_service")

### Repository examples - yes, its that simple :D
- User repository
![Alt text](https://i.pinimg.com/originals/cb/3f/41/cb3f41ab2a57cc61e5d076c31c0146ff.jpg?raw=true "user_repository")
- Feature repository
![Alt text](https://i.pinimg.com/originals/dc/73/61/dc73616f86bfe1d07cf586ce5f97f46d.jpg?raw=true "feature_repository")

