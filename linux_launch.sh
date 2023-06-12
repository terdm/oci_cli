export COMPARTMENT_ID=ocid1.tenancy.oc1..aaaaaaaafi7wsxmc6fwlqlcmcutm5l3aa4rxtytm2bfythnqd424obzfohiq
export AVAILABILITY_DOMAIN=$(oci iam availability-domain list --query "(data[?ends_with(name, '-3')] | [0].name) || data[0].name" --raw-output)
export VCN_ID=$(oci network vcn create -c ${COMPARTMENT_ID} --cidr-block "10.0.0.0/16" --query "data.id" --raw-output)

export SUBNET_ID=$(oci network subnet create --vcn-id ${VCN_ID} -c ${COMPARTMENT_ID} --cidr-block "10.0.0.0/24" --query "data.id" --raw-output)

export IG_ID=$(oci network internet-gateway create -c ${COMPARTMENT_ID} --is-enabled true --vcn-id ${VCN_ID} --query "data.id" --raw-output)

export RT_ID=$(oci network route-table list -c ${COMPARTMENT_ID} --vcn-id ${VCN_ID} --query "data[0].id" --raw-output)

oci network route-table update --rt-id ${RT_ID} --route-rules '[{"cidrBlock":"0.0.0.0/0","networkEntityId":"'${IG_ID}'"}]' --force

export USER_HOME=/home/terdm

#ssh-keygen -t rsa -N "" -b 2048 -C "CiCd-Compute-Instance" -f ${USER_HOME}/.ssh/id_rsa

export COMPUTE_SHAPE=VM.Standard.E2.1.Micro

export COMPUTE_OCID=$(oci compute instance launch \
 -c ${COMPARTMENT_ID} \
 --shape "${COMPUTE_SHAPE}" \
 --display-name "${COMPUTE_NAME}" \
 --image-id ocid1.image.oc1.eu-frankfurt-1.aaaaaaaaaddpb3f6u7bcdu2tcf4y7te6thy27vggvgcah7mklxyqxdtvic6q \
 --ssh-authorized-keys-file "${USER_HOME}/.ssh/id_rsa.pub" \
 --subnet-id ${SUBNET_ID} \
 --availability-domain "${AVAILABILITY_DOMAIN}" \
 --wait-for-state RUNNING \
 --query "data.id" \
 --raw-output)

echo $COMPUTE_OCID
export COMPUTE_IP=$(oci compute instance list-vnics \
  --instance-id "${COMPUTE_OCID}" \
  --query 'data[0]."public-ip"' \
  --raw-output)

echo $COMPUTE_IP

ssh -i /path/to/your/key/privateKeyName opc@${COMPUTE_IP}
