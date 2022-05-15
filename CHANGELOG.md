## 1.0.0 (2022-05-15)

#### Feature

* packaged the entire system into a helm chart (#9) (a2383827)
* **sherlock:** Added the logic to normalize data frame (8911c9b8)
* **inspector:** Integrated proxy with kubernetes (db10b669)
* **ui:** Created the  visualization dashboard (6b645bb0)
* **inspector:** Created Settings View (#6) (944aa131)
* **sherlock:** Created model inference pipeline (9154586b)
* **sherlock:** Added support for model reuse (3f5f223c)
* **control-plane:** Added support for sherlock module (c341c76c)
* **sherlock:** Implemented the Model pulling logic (b0d1c924)
* **sherlock:** Implemented the inferencing API (b2f07b57)
* **sherlock:** Implemented prometheus scraper (3372a5f9)
* **gazer:** Tracked request exchanges between services (08aa0534)
* **gazer:** Added support for ClusterIPs (81e98e76)
* **control-plane:** Implemented the core functionality (55fb9fae)
* **gazer:** Integrated with prometheus (#4) (656c660f)
* **gazer:** created TUI to visualize scraped data (e0c166aa)
* **gazer:** created a POC scraper using ebpf (088df5b9)

#### Bug Fixes

* **sherlock:** Optimzed the model (dc6414a3)
* **control-plane:** Models not registering (8f1a791a)
* **gazer:** Added backlog cleaner (9e527776)
* **gazer:** poll_kube_api exits after the first call (cc964e98)
* **sherlock:** logged missing metrics (f0fe3a92)
* **inspector:** Added missing Env file (3e6e9125)
* **inspector:** Typescript errors (41f1195b)
* **sherlock:** Moved poll_anomaly_scores sleep to async (5b49dbfc)
* **control-plane:** Fixed a pointer mixmatch (247ee288)
* **control-plane:** Fixed a bug in servings config generation (d802f0ad)
* **gazer:** Handle for units in metrics (562f72d2)
* **gazer:** Excluded TCP responses (93d0cab6)
* **gazer:** Handled for empty config.yaml (0a0e0d00)
* **control-plane:** Updated kubernetes manifest files (3361804d)

#### Documentation

* Added content to README.md (6de08e5d)
* **thesis:** completed the Project Specifications Design and Prototype (#5) (d0d5d0f2)
* added missing file proposal proposal files (8493b465)
* added the project proposal (#2) (5e8527dd)

#### Code Refactoring

* **sherlock:** Moved to single use tf-serving architecture (432a9df7)
* **sherlock:** moved the training code to a sub dir (ae099561)
* **control-plane:** Changed the serivce name variable (be3e074c)
* **control-plane:** Changed the controller Domain (d4b55887)

#### Chores

* created an action for releasing (0039dd1a)
* created script to profile the system (f2303f32)
* **deps:** bump moment from 2.29.1 to 2.29.2 in /ui (9927e9c3)
* Added a data collection agent (a46a587d)
* **CI:** Build only changed components (e97157f4)
* **control-plane:** Scaffolded the Control Plane (#3) (4259f886)
* **ci:** dockerize the gazer (f91305b0)

#### CI

* **inspector:** Fixed a misconfigured path (0333c60b)


