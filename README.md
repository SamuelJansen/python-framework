# python_framework - current on v0.1.8-2 - stable for python3.8 
Basically, its a Flask wrapper

It alters Flask behaviours in order to make APIs better organized.

I did it because it's cool and makes Flask better :D

## Features
- NOT A SINGLE SERIALIZER IS NEEDED!
- OpenApiDocumentation 
- JwtSecutiry
- Suport for services, validators, helpers, converters, mappers, and repository
- SqlAlhemyProxy without the need to "open connection" due to circular import issues. You call them and it works like a horse

### Requirements
- Add `python_framework==0.1.0.-05` in your `requirements.txt` file (or `python_framework==0.1.0.-post05`. In some environments, life is tuff)
- It comes with a lot of stuffs. Check on [setup.py](https://github.com/SamuelJansen/python_framework/blob/master/setup.py "setup.py"). If you need a different version of some of them, you can add it bellow `python_framework==0.1.0.-05`

Something like this:

```
python_framework==0.1.0.post05
sqlalchemy==9.9.9
etc==7.0.3
so_on_so_forth==1.0.2
```

### Package pattern 
- [This package pattern](https://github.com/SamuelJansen/FeatureManager "package_pattern") makes possible automatic controller registration, controller-service-repository-etc interconnections and so on. Just follow it and/or make improvement suggestions ("could be this way", "could be that way", etc)

![Package pattern](https://i.pinimg.com/originals/f6/b0/6a/f6b06aac4c675655a8ad8763f2afcbe4.jpg?raw=true "package_pattern")

### Globals.yml configuration file
- [Globals.yml](https://github.com/SamuelJansen/FeatureManager/blob/master/api/resource/Globals.yml "Globals.yml") configures the application 

[globals](https://github.com/SamuelJansen/globals "globals_module") module still requires some implementation in order to make OS variables income here. For while, it does not

![Globals.yml example](https://i.pinimg.com/originals/47/2f/d5/472fd582fac7483666e327e754be5df1.jpg?raw=true "globals_confituration_file")

### app.py and MyApi.py - just copy paste and be happy
[app.py](https://github.com/SamuelJansen/FeatureManager/blob/master/app.py "app.py")

[FeatureManager.py](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/FeatureManager.py "FeatureManager.py")

![app.py and MyApi.py](https://i.pinimg.com/originals/e8/99/ff/e899ff77f1ecde64bf22175422691e63.jpg?raw=true "app_and_MyApi")

### Documentation example
https://feature-dataset-manager.herokuapp.com/swagger/ - it may take a while to load as heroku sometime sleeps...

- No configurations needed. Just code you controllers and it will be there at `GET: whathever-your-host-is/basic-deploy-url/swagger` endpoint

### Controller examples
[Login controller](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/controller/authentication/LoginController.py "Login controller")

![Login controller example](https://i.pinimg.com/originals/46/ad/f1/46adf1c4209bf789ae6cbc63828fd003.jpg?raw=true "login_controller")

[Feature controller](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/controller/feature/FeatureController.py "Feature controller")

![Feature controller example](https://i.pinimg.com/originals/87/95/7d/87957d15526998de8ef4b587e8b89373.jpg?raw=true "feature_controller")

### Service examples
[User service](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/service/UserService.py "User service")

![User service](https://i.pinimg.com/originals/1b/77/54/1b7754ba9ba1067261aef67fead519bc.jpg?raw=true "user_service")

[Feature service](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/service/FeatureService.py "Feature service")

![Feature service](https://i.pinimg.com/originals/1b/77/54/1b7754ba9ba1067261aef67fead519bc.jpg?raw=true "feature_service")

### Repository examples - yes, its that simple :D
[User repository](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/repository/UserRepository.py "User repository")

![User repository](https://i.pinimg.com/originals/cb/3f/41/cb3f41ab2a57cc61e5d076c31c0146ff.jpg?raw=true "user_repository")

[Feature repository](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/repository/FeatureRepository.py "Feature repository")

![Feature repository](https://i.pinimg.com/originals/dc/73/61/dc73616f86bfe1d07cf586ce5f97f46d.jpg?raw=true "feature_repository")

### Model examples
[User model](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/model/User.py "User model")

![User model](https://i.pinimg.com/originals/29/75/24/29752451dc74cc2209e94bc0326f9eed.jpg?raw=true "user_model")

[Feature model](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/model/Feature.py "Feature model")

![Feature model](https://i.pinimg.com/originals/c2/4b/a9/c24ba93018bdd9229ccb164c7aa523e1.jpg?raw=true "feature_model")

[Model association](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/model/ModelAssociation.py "Model association") - its just to make things easier

![Model association](https://i.pinimg.com/originals/9d/59/ae/9d59ae37c24a5508e5a56d01e33c9378.jpg?raw=true "model_association")

### Mapper examples
[User mapper](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/mapper/UserMapper.py "User mapper")

![User mapper](https://i.pinimg.com/originals/2a/aa/81/2aaa811f38bd5ec22f2b5eab3858d9a4.jpg?raw=true "user_mapper")

[Feature mapper](https://github.com/SamuelJansen/FeatureManager/blob/master/api/src/mapper/FeatureMapper.py "Feature mapper")

![Feature mapper](https://i.pinimg.com/originals/d9/dc/77/d9dc771066877d75152b477557f0339a.jpg?raw=true "feature_mapper")

## Usage examples
- [FeatureManager API](https://github.com/SamuelJansen/FeatureManager "FeatureManager API")
- [WebkookBoot API](https://github.com/SamuelJansen/WebkookBoot "WebkookBoot API")

## Notes - stable for python3.8
### - v0.1.0-05 
### - v0.1.8-2
- Of course it's open source
- If you don't follow package pattern, it wont happens
- I just hate OS environments lose all over the project. That's why I made Globals.py, so we can centralize it in there. Unfortnatelly, `globals` module isn't perfect yet. That's my next goal
- Repository connections are much alike SqlAlchemy native sintax. So, any specific implementation can be written in SqlAlchemy native sintax. Any issue, contact me, so I can fix it.
- Same for migrations. Use any SqlAlchemy migrations engine you like. For `python_framework`, a liquibase migration like is being implemented, but won't be release before 2021, july 
- The auto-serialization stuff is just magic. But it comes with a price: Models and Dtos must have all its attributes initialyzed with None value. I'll fix it by 2021, february
- Yes, api code/file imports are simplifyed. You can move a service from one package to another without impact on API behaviour. Just make shure it's somewhere inside the `service` package.
- Unit tests requires instance injection in runtime. I'm implementing a module to handle it, so as its Mocks. It will be release by 2021, february
- `python_framework` comes with a LogError table by default (an auditory like stuff for api errors or bad behaviours). Contact me if you don't want it, so I'll release a feature to enable it only when it's actually desired
- Any issues with deploy, contact me so I can fix it
- I may release further versions. Don't use them before a proper release here
- Of course this wrapper may have bugs. Whenever you find one, issue it here. So I can fix it and make it better :D
