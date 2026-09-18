from .job import Job, JobFn

class JobFactory:
  """
  Instance (that must be a singleton) used to create `Job` instances.  
  
  This class is necessary to:  
  - issue `job.id` with a unique value  
  
  **IMPORTANT**: do not create `Job` directly, use `JobFactory.createJob(...)`.
  """
  def __init__(self):
    self._id_generator = JobIdGenerator()
  def createJob(
    self, 
    title: str, 
    stepsTotal: int, 
    jobFn: JobFn,
  ):
    jobId = str(self._id_generator.generate())
    job = Job(
      id=jobId, 
      title=title, 
      stepsTotal=stepsTotal, 
      jobFn=jobFn
    )
    return job
    
    
class JobIdGenerator:
  def __init__(self):
    self.id = 0
  def generate(self):
    self.id += 1
    return self.id