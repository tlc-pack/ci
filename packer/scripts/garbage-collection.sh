BACKLOG_SIZE=50
for i in "$@"
do
  IMAGE_FAMILY=$i
  STALE_IMAGES=$(gcloud compute images list --filter="family=${IMAGE_FAMILY}"\
   --format="value(name)" --sort-by=~creationTimestamp|tail -n +${BACKLOG_SIZE})
  for j in $STALE_IMAGES
  do
    gcloud compute images delete $j --quiet
  done
done

