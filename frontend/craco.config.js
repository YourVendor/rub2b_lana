module.exports = {
    webpack: {
      configure: (webpackConfig) => {
        return webpackConfig;
      },
    },
    devServer: {
      setupMiddlewares: (middlewares, devServer) => {
        // Кастомная логика, если нужно
        return middlewares;
      },
    },
  };