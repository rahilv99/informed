from celery_app import celery_app

@celery_app.task
def step_one():
    print("Step One: Started")
    return "Step One Completed"

@celery_app.task
def step_two(data):
    print(f"Step Two: Received {data}")
    return f"Step Two Completed with {data}"

@celery_app.task
def step_three(data):
    print(f"Step Three: Received {data}")
    return f"Pipeline Finished with {data}"

@celery_app.task
def main_pipeline():
    print("Main Pipeline: Started")
    chain = step_one.s() | step_two.s() | step_three.s()
    result = chain.apply_async()
    print(f"Pipeline triggered with task ID: {result.id}")
