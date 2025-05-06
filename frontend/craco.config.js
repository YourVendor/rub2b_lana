module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      return webpackConfig;
    },
  },
  devServer: {
    setupMiddlewares: (middlewares, devServer) => {
      if (!devServer) {
        throw new Error('webpack-dev-server is not defined');
      }
      // Custom middleware logic here
      return middlewares;
    },
  },
};