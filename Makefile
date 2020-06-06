PACKAGED_TEMPLATE = packaged.yaml
S3_BUCKET := pullreminders2
STACK_NAME := pullreminders2
TEMPLATE = template.yaml

.PHONY: lint
lint:
	pylint app tests/unit

.PHONY: fixcode
fixcode:
	autopep8 --in-place --aggressive --aggressive --recursive app tests/unit



.PHONY: build
build:
	sam build --manifest app/requirements.txt

.PHONY: api
api: build
	sam local start-api

.PHONY: package
package: build
	sam package --s3-bucket $(S3_BUCKET) --output-template-file $(PACKAGED_TEMPLATE)

.PHONY: deploy
deploy: package
	sam deploy --stack-name $(STACK_NAME) --template-file $(PACKAGED_TEMPLATE) --capabilities CAPABILITY_IAM

.PHONY: describe-stack
describe-stack: 
	aws cloudformation describe-stack-events --stack-name pullreminders2


.PHONY: validate
validate: validate
	sam validate

