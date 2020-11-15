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
- [This package pattern](https://github.com/SamuelJansen/FeatureManager "package_pattern") automate controller registration, controller-service-repository-etc interconnections and so on

![Package pattern](https://i.pinimg.com/originals/f6/b0/6a/f6b06aac4c675655a8ad8763f2afcbe4.jpg?raw=true "package_pattern")

### Globals.yml configuration file
- [Globals.yml](https://github.com/SamuelJansen/FeatureManager/blob/master/api/resource/Globals.yml "Globals.yml") configures the application 

I still need to do some work on globals library in order to make OS variables income here. For while it does not

![Globals.yml example](https://i.pinimg.com/originals/47/2f/d5/472fd582fac7483666e327e754be5df1.jpg?raw=true "globals_confituration_file")

### app.py and MyApi.py - just copy paste and be happy
![app.py and MyApi.py](https://i.pinimg.com/originals/e8/99/ff/e899ff77f1ecde64bf22175422691e63.jpg?raw=true "app_and_MyApi")

### Documentation example
https://feature-dataset-manager.herokuapp.com/swagger/ - it may take a while to load as heroku sometime sleeps...

### Controller examples
- Login controller

![Login controller example](https://i.pinimg.com/originals/46/ad/f1/46adf1c4209bf789ae6cbc63828fd003.jpg?raw=true "login_controller")

- Feature controller

![Feature controller example](https://i.pinimg.com/originals/87/95/7d/87957d15526998de8ef4b587e8b89373.jpg?raw=true "feature_controller")

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

### Model examples
- User model

![Alt text](https://i.pinimg.com/originals/29/75/24/29752451dc74cc2209e94bc0326f9eed.jpg?raw=true "user_model")

- Feature model

![Alt text](https://i.pinimg.com/originals/c2/4b/a9/c24ba93018bdd9229ccb164c7aa523e1.jpg?raw=true "feature_model")

- Model association - its just to make things easier

![Alt text](https://i.pinimg.com/originals/9d/59/ae/9d59ae37c24a5508e5a56d01e33c9378.jpg?raw=true "model_association")

### Mapper examples
- User mapper

![Alt text](https://i.pinimg.com/originals/2a/aa/81/2aaa811f38bd5ec22f2b5eab3858d9a4.jpg?raw=true "user_mapper")

- Feature mapper

![Alt text](https://i.pinimg.com/originals/d9/dc/77/d9dc771066877d75152b477557f0339a.jpg?raw=true "feature_mapper")
