#!/bin/bash
#
# 2019 CopyLeft, Catch-23 Team
# SVAI Research case: Undiagnosed-1
# rilson.nascimento@gmail.com

VCF_LOC="/root/notebooks/patient-data/WGS/DeepVariant_VCFs/"
VCF_FILE="SQ9887_L00.reheader.vcf.gz"
TABIX_OUTPUT_DIR="/root/parallel_tabix/tabix_output"

run_tabix() {
        RUN_ID=$1
        CHR_START_STOP=$2
        FILE_SUFFIX=`echo ${CHR_START_STOP} | sed 's/:/-/g'`

        echo "running tabix for ${CHR_START_STOP}"
        if [ -f "${TABIX_OUTPUT_DIR}/tabix_out_${FILE_SUFFIX}.txt" ]; then
                echo "tabix outfile file exists. skipping"
                return
        fi

        tabix -f ${VCF_LOC}/${VCF_FILE} ${CHR_START_STOP} > ${TABIX_OUTPUT_DIR}/tabix_out_${FILE_SUFFIX}.txt
}

##################### M A I N #########################

INPUT_FILE=$1
MAX_PAR=$2

RUN_ID=1
NPAR=0

if [ -z "${MAX_PAR}" ]; then
       MAX_PAR=5
fi

while read LINE; do
        CHR_START_STOP=${LINE}

        run_tabix $RUN_ID $CHR_START_STOP &
        ((RUN_ID++))
        ((NPAR++))

        if ((NPAR==MAX_PAR)); then
                sleep 2
                echo "*******************************************************************************"
                echo ">>> Max parallelization of $MAX_PAR reached. Waiting for current runs to finish"
                echo "*******************************************************************************"
                NPAR=0
                wait
        fi
done < $INPUT_FILE
