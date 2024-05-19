# board to build (in ./boards folder)
BOARD=ESP32_S3_N16R8

FROZEN_MANIFEST=src/freeze/manifest.py
VERSION_FILE=src/freeze/version.py
USER_C_MODULES=src/modules/micropython.cmake
PORT_DIR=micropython/ports/esp32
BUILD_DIR=${PORT_DIR}/build-${BOARD}
FIRMWARE_DIR=firmware/${BOARD}/$(shell date +%Y%m%d-%H%M%S)
LATEST_FIRMWARE_DIR=firmware/${BOARD}/latest
GITHUB_REPOSITORY=iot49/leaf
IDF_VERSION=v5.0.4

tag := $(shell date +"%Y.%m.%d")


.PHONY: build dependencies flash

build: dependencies clean
	@echo "!!! LOCAL BUILD broken - evenbus not mapped !!!"
	echo "TAG = '${tag}'\nBOARD = '${BOARD}'\nGITHUB_REPOSITORY = '${GITHUB_REPOSITORY}'\nIDF_VERSION = '${IDF_VERSION}'" > ${VERSION_FILE}
	docker run --rm \
		-v .:/project -w /project/micropython \
		espressif/idf:${IDF_VERSION} \
		bash -c " \
			make -C mpy-cross; \
			cd ports/esp32; \
			make BOARD=${BOARD} clean; \
			make V=1 \
				BOARD=${BOARD} \
				USER_C_MODULES=/project/${USER_C_MODULES} \
				FROZEN_MANIFEST=/project/${FROZEN_MANIFEST}"
	@echo Copied compiled firmware is in ${FIRMWARE_DIR}
	mkdir -p ${FIRMWARE_DIR}
	cp ${BUILD_DIR}/{firmware.bin,micropython.bin,micropython.uf2} ${FIRMWARE_DIR}
	mkdir -p ${LATEST_FIRMWARE_DIR}
	cp ${BUILD_DIR}/{firmware.bin,micropython.bin,micropython.uf2} ${LATEST_FIRMWARE_DIR}
	@echo Cleaning up
	rm -rf ${PORT_DIR}/build-${BOARD}
	rm -rf ${PORT_DIR}/boards/${BOARD}
	rm ${PORT_DIR}/partitions-S3*

dependencies:
	git submodule update --init micropython
	make -C ${PORT_DIR} submodules
	cd micropython; git submodule update --init lib/berkeley-db-1.xx lib/micropython-lib
	make -C micropython/ports/esp32 submodules
	cp -a boards $(PORT_DIR)
	# Hack: sometimes (???) idf looks for custom partition table in PORT_DIR
	cp ${PORT_DIR}/boards/${BOARD}/partition* ${PORT_DIR}

flash:
	@ls /dev/*usb*
	esptool.py erase_flash
	esptool.py --chip esp32s3 write_flash -z 0 firmware/${BOARD}/latest/firmware.bin

flash-download:
	@ls /dev/*usb*
	esptool.py erase_flash
	esptool.py --chip esp32s3 write_flash -z 0 ~/Downloads/UM_PROS3*.bin

clean:
	@echo "Removing python cache files..."
	find ../.. -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
