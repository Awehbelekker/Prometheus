module.exports = {
  stories: ['../components/**/*.stories.@(tsx|mdx)'],
  addons: ['@storybook/addon-essentials','@storybook/addon-interactions'],
  framework: {
    name: '@storybook/react-webpack5',
    options: {}
  },
};
