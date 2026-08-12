# Asset License

The pet sprite sheets in `src/codepet/assets/` and their source copies in `assets/`
were generated specifically for CodePet using OpenAI's image generation tool. They
are original project assets and do not reproduce Bongo Cat artwork or another
existing game character.

Files in `assets/concepts/` are non-production animation studies generated with the
built-in image-generation mode. They failed the project's exact grid or frame-count
review and are intentionally not loaded by the application. The prompts requested
an original warm pixel-art Ragdoll cat, chroma-key green background, and six rows of
eight poses for idle, walk, run, eat, affection, and sleep; the second prompt asked
to preserve the design while correcting missing cells. Production animation atlases
must be manually redrawn and reviewed under `assets/animations/README.md`.

The six breed atlases in `assets/animations/*.png` and
`src/codepet/assets/animations/*.png` were created for CodePet with the built-in
OpenAI image-generation mode, then chroma-keyed, split, normalized, cleaned, visually
reviewed, and validated by the project scripts. The prompt set requested original
breed identities and six eight-frame clips—idle, walk, run, eat, affection, and
sleep—while explicitly prohibiting copying or tracing Bongo Cat, Stardew Valley, or
another game sprite.

These assets may be used, modified, and redistributed as part of CodePet and CodePet forks under the same MIT terms as the repository. Third-party replacement skins must include clear authorship and licensing information.
