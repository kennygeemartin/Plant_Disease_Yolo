# Source-document audit

## Materials reviewed

- `Editors Decision2.docx` — decision letter, Reviewer 1, Reviewer 2, and editorial requirements.
- `Intelligent Plant Disease Detection System REVISED TWO.docx` — revised manuscript, claims, figures/tables, methods, results, and bibliography.
- `JohnNwodo -Modeling of IoT-based system for plant disease detection and management using deep transfer learning techniques-PostOral.pdf` — related thesis/report, including its methods, reported results, and appendix code.

No separate image directory, PlantVillage download, local field-image archive, Roboflow export, YOLOv10 source tree, trained checkpoint, training logs, or IoT device/notification logs were present in the folder.

## Additional evidence from the related PDF

The PDF provides context, but it does not supply the missing dataset or a verifiable YOLOv10 run:

1. Its abstract (printed p. 7) describes 200 epochs, while the training section (printed p. 66) says 300 epochs. The results table (printed pp. 73–78) ends at epoch 149. The revised manuscript says 150 epochs. These are inconsistent accounts, not an original run log.
2. The training section (printed p. 66) describes a Windows 10 system with an NVIDIA GeForce RTX 3030Ti, a Core i9-12900 CPU, and 16 GB of graphics memory. The revised manuscript instead says Google Colab. No machine-readable run record corroborates either environment.
3. The appendix's “plant disease detection model” code (printed pp. 109–110) initializes `YOLO('yolov8n.pt')`, says YOLOv8, and shows an example of 100 epochs, batch 16, and 640-pixel input. The output printed beneath it identifies Ultralytics 8.2.58 and a Kaggle brain-tumour dataset. This is not evidence that the submitted YOLOv10 model was trained with that code or configuration.
4. The appendix dehazing functions (printed pp. 111–112) provide reproducible parameter values: a 15×15 dark-channel filter, top 0.1% candidates for atmospheric light, omega 0.95, and minimum transmission 0.1; the histogram function equalizes the Y channel in YUV. The preceding methods text describes a guided-filter refinement, but that appendix implementation contains no guided filter. The proxy uses the appendix implementation and discloses this mismatch.
5. The PDF repeats 2,141 local images and 54,303 PlantVillage images, but does not contain those images, the Roboflow export, a full source-wise/class-wise annotation inventory, pathologist or laboratory records, or partition IDs. The reproduced description is not a substitute for the underlying data.
6. The PDF describes field capture, SMTP notification, and qualitative testing but supplies no traceable image-transfer, inference, notification-delay, or end-to-end reliability measurements.

## Implication for the revision

The thesis supports recovery of some narrative implementation details only. Its contradictory epoch counts, hardware descriptions, and YOLOv8 example do not resolve the reviewers' request to verify the YOLOv10 implementation, historical metrics, or reproducibility. The experiment results in this package are from a separate public-data proxy.

## Manuscript issues requiring author action

- Do not retain the unsupported 91.1% precision, 85.9% recall, 88.4% F1, 90.8% mAP@0.5, 58.5% mAP@0.5:0.95, or 94% accuracy as newly verified facts. The source values cannot be reproduced from the supplied records.
- Remove the claim that disease detection is “early” unless there is a disease-stage-labelled, independently evaluated experiment. The thesis narrative about a farm with limited visible symptoms is not a model performance study by disease stage.
- Remove unmeasured claims of real-time performance, reliable field operation, or successful end-to-end notification unless device logs and trials are supplied.
- The revised manuscript's comparison table mislabels the cited Alsakar et al. YOLOv11n–DeiT work as YOLOv10n. The comparison values should be omitted until verified against the cited source.
- The revised manuscript cites Shueil et al., Dun et al., and Nnaedozie et al. without matching reference-list entries. Audit every citation and DOI against primary sources; do not infer missing bibliographic details.
- Original disease-label identities and the reported 56,444-image combined corpus remain unverified without the local image archive, PlantVillage annotation export, and expert-review records.
