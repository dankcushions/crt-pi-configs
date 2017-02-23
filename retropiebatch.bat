@echo off

python crt_pi_configs.py mame2003 1920 1080
python crt_pi_configs.py fbalpha 1920 1080
python crt_pi_configs.py consoles 1920 1080
python -c "import crt_pi_configs; crt_pi_configs.createZip(False,1920,1080)"

python crt_pi_configs.py mame2003 1366 768
python crt_pi_configs.py fbalpha 1366 768
python crt_pi_configs.py consoles 1366 768
python -c "import crt_pi_configs; crt_pi_configs.createZip(False,1366,768)"

python crt_pi_configs.py mame2003 1280 720
python crt_pi_configs.py fbalpha 1280 720
python crt_pi_configs.py consoles 1280 720
python -c "import crt_pi_configs; crt_pi_configs.createZip(False,1280,720)"

python crt_pi_configs.py mame2003 1280 1024
python crt_pi_configs.py consoles 1280 1024
python crt_pi_configs.py fbalpha 1280 1024
python -c "import crt_pi_configs; crt_pi_configs.createZip(False,1280,1024)"

python crt_pi_configs.py mame2003 curvature 0
python crt_pi_configs.py fbalpha curvature 0
python -c "import crt_pi_configs; crt_pi_configs.createZip(True)

pause