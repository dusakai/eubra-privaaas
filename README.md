## PrivaaaS - EUBra-BISEA

PrivaaaS is a set of libraries and tools developed in python that allow controlling and reducing data leakage in the context of Big Data processing and, consequently, protecting sensitive information that is processed by analytics algorithms.
In this version, you can apply data anonymization techniques on a set of tables according to anonymization policies. The PRIVAaaS provides generalization, suppression, masking, and encryption techniques. It is possible to apply the conjunction and disjunction process in the policies, in order to have a more or less restrictive data anonymization. The conjunction process applies an "AND" operation in the policies fields, anonymizing only the fields in the raw data which have a corresponding one in all policies. It means that, in this phase,  the least restrictive policies were considered, hence maximizing data utility.  The disjunction process applies an “OR” operation in the policies fields, which implies that all the fields must be anonymized according to their respective policies. This disjunction process results in the most restrictive anonymization, guaranteeing that the protection established by the policies are accomplished, performing the necessary anonymization to better protect the data.
In addition, the ARX library was integrated into the PrivaaaS to calculate the re-identification risk and, according to a risk threshold, to apply the k-anonymity algorithm to increase the anonymity level.
The python application allows csv and json files, both as input to the database and policies, as well as output format files. After calculating the risk and applying the k-anonymity algorithm by ARX the output dataset will be in csv format.
An initial user interface was implemented to manipulate the files and you can also use PrivaaaS as a service accessing the form with curl command line. Thus, the PrivaaaS can be used by other applications even if they were developed using  different programming languages.

To run PrivaaaS, you only need install Docker, and after that the process is fully automated.

On Linux or Mac, run the Docker-build.sh and Docker-run.sh files:

## Build the Docker image

$ source Docker-build.sh

## Run Docker

$ source Docker-run.sh

## Visit the site:

http://localhost:5000

To run on Windows see the documentation in https://docs.docker.com/docker-for-windows/ to build Docker container and run it.

--
EUROPE - BRAZIL COLLABORATION OF BIG DATA SCIENTIFIC RESEARCH THROUGH CLOUD-CENTRIC APPLICATIONS. EUBra-BIGSEA. 2017.
