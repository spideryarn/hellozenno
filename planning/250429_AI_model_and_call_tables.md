# AI Model and Call Tables

## Goal, Context

Create a database structure to track AI model usage in the HelloZenno application. This involves:

1. Creating an `ai_model` table to store information about AI models used by the system
2. Creating an `ai_call` table to track individual calls to AI models

This tracking will help with:
- Measuring and monitoring AI usage costs
- Analyzing performance metrics
- Understanding user-triggered AI interactions
- Auditing AI model responses

## Principles, Key Decisions

- Both tables will inherit from BaseModel, providing them with primary keys, created_at, and updated_at timestamps
- Tables will use JSONField for `extra` to maintain flexibility for future requirements
- Foreign key relationships will use on_delete="CASCADE" for data integrity
- All performance metrics (tokens, duration) will be stored as part of the call record
- Cost tracking will be included to monitor expenses

## Useful References

- **migrations/032_add_various_fields.py** - Recent example migration adding fields to existing tables (HIGH)
- **docs/MIGRATIONS.md** - Guidelines for creating migrations (HIGH)
- **docs/DATABASE.md** - Database structure overview and connection information (MEDIUM)
- **db_models.py** - Current model definitions to match style and structure (HIGH)
- **utils/db_connection.py** - Database connection management (LOW)

## Actions

- [ ] Create a new migration file for the AI model tracking tables
  - [ ] Run `python -m utils.migrate create add_ai_model_and_call_tables`
  - [ ] Implement the migration file with table creation statements
  - [ ] Include rollback function to drop tables if needed

- [ ] Implement the `ai_model` table with the following fields:
  - [ ] `modelname` (CharField) - The name of the AI model
  - [ ] `version` (CharField) - Model version information
  - [ ] `extra` (JSONField) - Additional parameters/configurations

- [ ] Implement the `ai_call` table with the following fields:
  - [ ] `model` (ForeignKeyField to AIModel) - Reference to the model used
  - [ ] `prompt` (TextField) - The prompt sent to the model
  - [ ] `response` (JSONField) - The response received from the model
  - [ ] `input_tokens` (IntegerField, null=True) - Number of input tokens
  - [ ] `reasoning_tokens` (IntegerField, null=True) - Number of tokens used in reasoning
  - [ ] `output_tokens` (IntegerField, null=True) - Number of output tokens
  - [ ] `cost_usd` (FloatField, null=True) - Cost of the call in USD
  - [ ] `duration_ms` (IntegerField, null=True) - Duration of the call in milliseconds
  - [ ] `call_type` (CharField, null=True) - Purpose/category of the call
  - [ ] `status` (CharField, null=True) - Status of the call (success/error)
  - [ ] `user_id` (UUIDField, null=True) - Reference to the user who initiated the call
  - [ ] `extra` (JSONField) - Additional call parameters/metadata

- [ ] Update db_models.py to include the new model definitions
  - [ ] Add AIModel class definition
  - [ ] Add AICall class definition
  - [ ] Add both models to the get_models() function

- [ ] Run the migration locally to verify it works
  - [ ] Execute `./scripts/local/migrate.sh`
  - [ ] Check that tables are created correctly

- [ ] Create basic utility functions for logging AI calls
  - [ ] Function to record an AI call with all relevant metrics
  - [ ] Function to retrieve statistics on AI usage

## Appendix

### Proposed Table Structures

```python
# AIModel table
class AIModel(BaseModel):
    modelname = CharField()  # e.g., "gpt-4", "claude-3-sonnet"
    version = CharField()  # e.g., "0125", "20240229"
    extra = JSONField(default=dict)  # Additional parameters/configurations

    class Meta:
        indexes = ((("modelname", "version"), True),)  # Unique composite index

# AICall table
class AICall(BaseModel):
    model = ForeignKeyField(AIModel, backref="calls", on_delete="CASCADE")
    prompt = TextField()  # The prompt sent to the model
    response = JSONField()  # The response from the model
    input_tokens = IntegerField(null=True)  # Number of tokens in the input
    reasoning_tokens = IntegerField(null=True)  # Number of tokens used in reasoning
    output_tokens = IntegerField(null=True)  # Number of tokens in the output
    cost_usd = FloatField(null=True)  # Cost in USD
    duration_ms = IntegerField(null=True)  # Duration in milliseconds
    call_type = CharField(null=True)  # Purpose of the call (e.g., "translation", "metadata")
    status = CharField(null=True)  # Success, error, etc.
    user_id = UUIDField(null=True)  # Reference to auth.users
    extra = JSONField(default=dict)  # Additional call parameters
```

### Example Usage

```python
# Recording an AI call
def record_ai_call(modelname, version, prompt, response, metrics, call_type=None, user_id=None):
    # Get or create the AI model
    ai_model, _ = AIModel.get_or_create(modelname=modelname, version=version)
    
    # Create the AI call record
    AICall.create(
        model=ai_model,
        prompt=prompt,
        response=response,
        input_tokens=metrics.get('input_tokens'),
        reasoning_tokens=metrics.get('reasoning_tokens'),
        output_tokens=metrics.get('output_tokens'),
        cost_usd=metrics.get('cost_usd'),
        duration_ms=metrics.get('duration_ms'),
        call_type=call_type,
        status=metrics.get('status', 'success'),
        user_id=user_id,
        extra=metrics.get('extra', {})
    )
```