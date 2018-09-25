#### Steps to install on edX platform:

- Update github.in i.e
  - `-e git+https://github.com/amir-qayyum-khan/git_auto_export_sample.git@v0.1#egg=git-auto-export-sample==0.1`
- Update cms/envs/common. Append **INSTALLED_APPS**
    ```    
    # git auto export
    'git_auto_export',
    ```
- Go to `cms/djangoapps/contentstore/signals/handlers.py` and edit signal `listen_for_course_publish`.
  - And append: 
 
  ```
  try:
      from git_auto_export import run_auto_git_export
      run_auto_git_export(course_key)
  except (ImportError,  Exception) as error:
      log.exception(error)
  ``` 
- Now restart application.
- open cms.env and lms.env or private.py and set FEATURES flags
  
  ```
  "FEATURES": {
    "ENABLE_EXPORT_GIT": true,
    "ENABLE_GIT_AUTO_EXPORT": true
  }
  ```
 

#### SetUp CMS for git export:
- 