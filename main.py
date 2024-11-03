
import argparse
import yaml
if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('--config',type=str)
  args = parser.parse_args()

  with open(args.config,'r') as f:
    config = yaml.safe_load(f)

  for episode in config['episodes']:
    run_episode(episode,config)


