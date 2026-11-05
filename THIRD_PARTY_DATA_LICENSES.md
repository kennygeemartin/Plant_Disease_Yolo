# Third-party dataset licenses and attribution

The generated proxy data contains image copies and derived annotations from these
third-party sources. This note records the available license metadata; it is not legal
advice. Check source terms again before publishing or redistributing data.

## PlantVillage

- Dataset: [geraldmc/plantvillage-full](https://huggingface.co/datasets/geraldmc/plantvillage-full), revision `f808f2706d3ce50ce14652d2b6863d3cc30cf9c4`.
- License stated on the dataset card: CC0-1.0.
- Original publication: Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). Using deep learning for image-based plant disease detection. *Frontiers in Plant Science*, 7, 1419. https://doi.org/10.3389/fpls.2016.01419.
- The proxy's full-frame boxes are derived labels, not original lesion annotations.

## PlantDoc detection

- Dataset: [Project-AgML/plant_doc_detection](https://huggingface.co/datasets/Project-AgML/plant_doc_detection), revision `0bed0b75b3f0e563d21b6a4e69d15da21b245986`.
- The Hugging Face dataset card does not state a license. AgML's [source registry at commit `f0e0135c7fbd425e7e329b9ac45186cdaf03a47b`](https://github.com/Project-AgML/AgML/blob/f0e0135c7fbd425e7e329b9ac45186cdaf03a47b/agml/_assets/source_citations.json) identifies `plant_doc_detection` as CC BY-SA 4.0. Retain attribution and apply the license's share-alike terms to adapted material; resolve any inconsistency with the dataset maintainer before redistribution.
- AgML's [preprocessor at the same commit](https://github.com/Project-AgML/AgML/blob/f0e0135c7fbd425e7e329b9ac45186cdaf03a47b/agml/_internal/preprocess.py) reads PlantDoc annotations as `xmin, ymin, width, height` and converts them to COCO boxes. The proxy uses this same pixel-coordinate interpretation.
- Original publication: Singh, D., Jain, N., Jain, P., Kayal, P., Kumawat, S., & Batra, N. (2020). PlantDoc: A Dataset for Visual Plant Disease Detection. In *Proceedings of the 7th ACM IKDD CoDS and 25th COMAD*, 249–253. https://doi.org/10.1145/3371158.3371196.
