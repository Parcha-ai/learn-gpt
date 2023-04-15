# learn-gpt


# Server
First, ensure you're using poetry shell
```
poetry install # as needed
poetry shell
```

## Running the server
```
python run.py
```

## Running local streamlit
```
streamlit run st.py
```

## Running a test goal
```
python gen_plan.py
```

### CURL requests

```
# Create a plan
curl --request POST --header "Content-Type: application/json" --data '{"goal":"I want to learn how to golf"}' http://localhost:5001/v1/create_plan

# Get a plan
curl --request POST --header "Content-Type: application/json" --data '{"id":"<id>"}' http://localhost:5001/v1/get_plan
```